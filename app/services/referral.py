from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.referral import Referral
from app.models.user import User
from app.core.exceptions import AppException, ErrorCode
from typing import Optional
from app.utils.functions import generate_referral_code
from log import logger


class ReferralService:
    def __init__(self, db: Session):
        self.db = db

    def get_referral_by_user_id(self, user_id: str) -> Referral:
        return self.db.query(Referral).filter_by(owner_id=user_id).first()

    def create_referral(self, user_id: str) -> Referral:
        """
        Tạo referral code mới cho user
        """
        try:
            # Check if referral code already exists
            # referral = self.get_referral_by_user_id(user_id)
            # logger.info(f"Referral: {referral}")
            # if referral:
            #     raise AppException(
            #         error_code=ErrorCode.REFERRAL_ALREADY_EXISTS.value,
            #         message=ErrorCode.REFERRAL_ALREADY_EXISTS.name,
            #         status_code=400,
            #     )
            # Tìm user theo user_id

            # user = self.db.query(User).filter_by(id=user_id).first()
            # if not user:
            #     raise AppException(
            #         error_code=ErrorCode.USER_NOT_FOUND.value,
            #         message=ErrorCode.USER_NOT_FOUND.name,
            #         status_code=404,
            #     )

            # Tạo referral và liên kết với user
            referral_model = Referral(
                owner_id=user_id, referral_code=generate_referral_code()
            )
            print(referral_model)
            self.db.add(referral_model)
            # self.db.commit()
            return referral_model

        except IntegrityError as e:
            self.db.rollback()
            # Xử lý trùng lặp referral code (nếu có unique constraint)
            print(e)
            if "duplicate key value" in str(e):
                raise AppException(
                    error_code=ErrorCode.DUPLICATE_ENTRY.value,
                    message=ErrorCode.DUPLICATE_ENTRY.name,
                    status_code=409,
                )
            raise AppException.from_exception(e)

        except Exception as e:
            self.db.rollback()
            raise AppException(
                error_code=ErrorCode.INTERNAL_ERROR.value,
                message=ErrorCode.INTERNAL_ERROR.name,
                status_code=500,
                extra={"original_error": str(e)},
            )

    def get_all_referrals(self) -> list[Referral]:
        """Lấy danh sách tất cả referral"""
        return self.db.query(Referral).all()

    def use_ref_code(self, user_id: str, ref_code: str) -> None:
        """
        Sử dụng referral code
        """
        try:
            # Kiểm tra user
            user: User = self.db.query(User).get(user_id)
            if not user:
                raise AppException(
                    error_code=ErrorCode.NOT_FOUND.value,
                    message=ErrorCode.NOT_FOUND.name,
                    status_code=404,
                )
            # Tìm referral code
            referral: Referral = (
                self.db.query(Referral).filter_by(referral_code=ref_code).first()
            )
            if not referral:
                raise AppException(
                    error_code=ErrorCode.REFERRAL_NOT_FOUND.value,
                    message=ErrorCode.REFERRAL_NOT_FOUND.name,
                    status_code=404,
                )
            # Check if user_id is owner of referral
            if user_id == referral.owner_id:
                raise AppException(
                    error_code=ErrorCode.REFERRAL_NOT_OWNER.value,
                    message=ErrorCode.REFERRAL_NOT_OWNER.name,
                    status_code=400,
                )
            # Kiểm tra user đã trong danh sách chưa
            if user_id in (referral.referred_user_ids or []):
                raise AppException(
                    error_code=ErrorCode.REFERRAL_ALREADY_USED.value,
                    message=ErrorCode.REFERRAL_ALREADY_USED.name,
                    status_code=400,
                )

            # Cập nhật thông tin
            user.used_ref_code = ref_code
            referral.referred_user_ids = (referral.referred_user_ids or []) + [user_id]

            self.db.commit()

        except AppException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise AppException(
                error_code=ErrorCode.INTERNAL_ERROR.value,
                message=ErrorCode.INTERNAL_ERROR.name,
                status_code=500,
                extra={"original_error": str(e)},
            )
