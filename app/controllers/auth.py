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


class AuthController:
    def __init__(self, db: Session):
        self.db = db

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
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now() + timedelta(days=7)},
            settings.JWT_SECRET,
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
                settings.JWT_SECRET,
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
