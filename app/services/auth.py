import base64
import hashlib
import secrets
import requests
from typing import Dict, Optional
from app.utils.functions import create_jwt_token
from config import settings
from log import logger


class AuthService:
    def __init__(self):
        self.x_client_id = settings.X_CLIENT_ID
        self.x_client_secret = settings.X_CLIENT_SECRET
        self.x_redirect_uri = settings.X_REDIRECT_URI

    def generate_x_oauth_params(self) -> dict:
        """Generate OAuth parameters for X login"""
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )

        return {
            "state": state,
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
        }

    def handle_x_callback(self, code: str, code_verifier: str) -> Dict:
        """Handle the OAuth2 callback from X"""
        try:
            # Exchange authorization code for tokens
            token_url = "https://api.x.com/2/oauth2/token"

            auth_string = base64.b64encode(
                f"{self.x_client_id}:{self.x_client_secret}".encode()
            ).decode()

            headers = {
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {
                "code": code,
                "grant_type": "authorization_code",
                "client_id": self.x_client_id,
                "redirect_uri": self.x_redirect_uri,
                "code_verifier": code_verifier,
            }

            # Get tokens
            token_response = requests.post(token_url, headers=headers, data=data)
            token_data = token_response.json()
            logger.debug(f"Token response: {token_data}")

            if "error" in token_data:
                logger.error(f"Error getting tokens: {token_data}")
                raise ValueError(f"Error getting tokens: {token_data['error']}")

            # Get user info using the access token
            user_url = "https://api.twitter.com/2/users/me"
            user_headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
            }
            params = {"user.fields": "id,name,username,profile_image_url"}

            logger.debug(f"Making user info request to: {user_url}")
            logger.debug(f"User headers: {user_headers}")

            user_response = requests.get(user_url, headers=user_headers, params=params)
            logger.debug(f"User response status: {user_response.status_code}")
            logger.debug(f"User response text: {user_response.text}")

            user_data = user_response.json()
            if "data" not in user_data:
                logger.error(f"Unexpected user data format: {user_data}")
                raise ValueError("Invalid user data received from X")

            user = user_data["data"]

            # TODO: save user to db
            logger.debug(f"User: {user}")
            # Create JWT token for our system
            jwt_token = create_jwt_token(
                {
                    "user_id": user["id"],
                    "username": user["username"],
                    "name": user["name"],
                    "picture": user.get("profile_image_url"),
                }
            )
            logger.debug(f"JWT token: {jwt_token}")
            return {
                "token": jwt_token,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "name": user["name"],
                    "picture": user.get("profile_image_url"),
                },
            }

        except Exception as e:
            logger.error(f"Error during X callback: {str(e)}")
            raise ValueError(f"Failed to process X callback: {str(e)}")


auth_service = AuthService()
