from app.dto import UseRefCodeRequest
from sqlalchemy.orm import Session
from app.services.referral import ReferralService
from fastapi import HTTPException
from app.models.user import User
from app.core.exceptions import AppException
from app.core.response import ResponseHandler


class ReferralController:
    def __init__(self, db: Session):
        self.db = db
        self.referral_service = ReferralService(db)

    def use_ref(self, body: UseRefCodeRequest, user: User):
        user_id = user.id
        try:
            self.referral_service.use_ref_code(user_id, body.ref_code)
            return ResponseHandler.success(message="Referral code used successfully")
        except AppException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "message": e.message,
                    "code": e.error_code,
                },
            )
