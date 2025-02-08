from app.dto import LoginRequest, SignupRequest
from sqlalchemy.orm import Session
from app.services.user import UserService
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt
from config import settings
from app.services.wallet import WalletService
from app.dto import SocialCallbackRequest
from app.services.referral import ReferralService
from log import logger
from app.utils.functions import generate_uuid
from app.services.auth import auth_service
from config import settings
from app.utils.functions import verify_jwt_token, create_jwt_token
from app.middleware.redis import get_redis_client
from app.dto import UserRequestDTO


class AuthController:
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = get_redis_client()

    def login(self, body: LoginRequest):
        user_service = UserService(self.db)
        user = user_service.get_user_by_email(body.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        if not user.password == body.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        # TODO: Generate JWT token
        token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now() + timedelta(hours=1)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now() + timedelta(days=7)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        # TODO: Return JWT token
        return {
            "message": "Login successful",
            "access_token": token,
            "refresh_token": refresh_token,
        }

    def signup(self, body: SignupRequest):
        user_service = UserService(self.db)
        user = user_service.get_user_by_email(body.email)
        if user:
            raise HTTPException(status_code=401, detail="User already exists")
        body.avatar = (
            body.avatar
            or f"https://avatar.iran.liara.run/username?username={body.username}"
        )
        user = user_service.create_user(body)
        # Create wallet
        wallet_service = WalletService(self.db)
        wallet = wallet_service.create_wallet(user.id)

        return {
            "message": "Signup successful",
            "wallet": {
                "public_key": wallet.public_key,
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "avatar": user.avatar,
            },
        }

    def callback_social(self, body: SocialCallbackRequest):
        user_service = UserService(self.db)
        wallet_service = WalletService(self.db)
        referral_service = ReferralService(self.db)

        # Set default avatar if not provided
        body.avatar = (
            body.avatar
            or f"https://avatar.iran.liara.run/username?username={body.username}"
        )

        # Get or create user
        try:
            # Start transaction
            self.db.begin()
            # Get or create user
            user = user_service.get_user_by_email(body.email)
            if not user:

                user = user_service.create_user(
                    body,
                    body.ref_code,
                )

                wallet = wallet_service.create_wallet(user.id)
            else:
                wallet = wallet_service.get_wallet_by_user_id(user.id)

            # Get or create referral
            referral = referral_service.get_referral_by_user_id(user.id)
            if not referral:
                referral = referral_service.create_referral(user.id)

            self.db.commit()
            # Generate JWT token
            token = jwt.encode(
                {"sub": str(user.id), "exp": datetime.now() + timedelta(hours=1)},
                settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM,
            )
            # Commit transaction

            return {
                "message": "Social callback successful",
                "access_token": token,
                "wallet": {"public_key": wallet.public_key},
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "avatar": user.avatar,
                },
                "referral": {
                    "code": referral.referral_code,
                    "total_used": referral.total_used,
                },
            }
        except Exception as e:
            # Rollback transaction in case of any error
            self.db.rollback()
            logger.error(f"Error during social callback: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error during social callback: {str(e)}"
            )

    def auth_x(self) -> str:
        """Initiate X OAuth2 flow"""
        # Generate OAuth parameters
        oauth_params = auth_service.generate_x_oauth_params()

        # Store state and verifier
        self.redis_client.set(oauth_params["state"], oauth_params["code_verifier"])
        self.redis_client.expire(oauth_params["state"], 60 * 5)
        # Construct X OAuth URL
        x_auth_url = (
            "https://x.com/i/oauth2/authorize"
            "?response_type=code"
            f"&client_id={settings.X_CLIENT_ID}"
            f"&redirect_uri={settings.X_REDIRECT_URI}"
            "&scope=tweet.read%20users.read"
            f"&state={oauth_params['state']}"
            f"&code_challenge={oauth_params['code_challenge']}"
            "&code_challenge_method=S256"
        )
        return x_auth_url

    def callback_x(self, code: str, state: str):
        code_verifier = self.redis_client.get(state)

        if not code_verifier:
            raise HTTPException(status_code=400, detail="Invalid state")

        try:
            result = auth_service.handle_x_callback(code, code_verifier)
            # Redirect to frontend with token
            frontend_url = f"{settings.FRONTEND_URL}/login?token={result['token']}"
            return frontend_url
        except Exception as e:
            logger.error(f"Error during X callback: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error during X callback: {str(e)}"
            )

    def login_x(self, token: str, ref_code: str = None):
        """Handle direct X token login"""
        try:
            # TODO: implement X token login using the access token
            idinfo = verify_jwt_token(token)

            # TODO: get user info from the access token
            user_id = idinfo["sub"]
            username = idinfo.get("username")
            name = idinfo.get("name")
            address = idinfo.get("address", "")
            # Create user
            user_service = UserService(self.db)
            user = user_service.get_user_by_email(username)
            logger.debug(f"User Exists: {user}")
            if not user:
                user_data = UserRequestDTO(
                    email=username,
                    username=username,
                )
                user = user_service.create_user(user_data, ref_code, user_id)
                logger.debug(f"User created: {user}")
            # Create wallet
            # wallet_service = WalletService(self.db)
            # wallet = wallet_service.get_wallet_by_user_id(user.id)
            # if not wallet:
            #     wallet = wallet_service.create_wallet(user.id)
            # Create referral
            referral_service = ReferralService(self.db)
            referral = referral_service.get_referral_by_user_id(user.id)
            if not referral:
                referral = referral_service.create_referral(user.id)
            # Commit transaction
            self.db.commit()
            # TODO: create JWT token for our system
            jwt_token = create_jwt_token(
                {"sub": user_id, "username": username, "name": name}
            )

            return {
                "token": jwt_token,
                "user": {
                    "id": user_id,
                    "username": username,
                    "name": name,
                    "avatar": user.avatar,
                    # "wallet": {"public_key": wallet.public_key},
                    "referral": {
                        "code": referral.referral_code,
                        "total_used": referral.total_used,
                    },
                },
            }
        except Exception as e:
            raise ValueError(f"Failed to process X token login: {str(e)}")
