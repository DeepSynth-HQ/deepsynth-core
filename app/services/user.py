from sqlalchemy.orm import Session
from app.models.user import User
from app.models.referral import Referral
from app.dto import UserRequestDTO
from app.core.exceptions import AppException, ErrorCode
from sqlalchemy.exc import IntegrityError
from app.utils.functions import generate_uuid


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self, user: UserRequestDTO, ref_code: str = None, id: str = None
    ) -> User:
        try:
            # Find refferral by ref_code
            referral = (
                self.db.query(Referral)
                .filter(Referral.referral_code == ref_code)
                .first()
            )
            # Generate user id
            id = generate_uuid() if id is None else id
            # Append user id to referral
            if referral:
                referral.referred_user_ids = referral.referred_user_ids + [id]
            else:
                # If referral not found, set ref_code to None
                ref_code = None
            user_data = user.model_dump()
            user_data["id"] = id
            user_data["used_ref_code"] = ref_code
            # Remove ref_code from user_data
            user_data.pop("ref_code", None)

            user_model = User(**user_data)

            self.db.add(user_model)
            # add referral
            if referral:
                self.db.add(referral)
            # self.db.commit()

            return user_model
        except IntegrityError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise AppException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message=str(e),
                status_code=500,
                extra={"original_error": str(e)},
            )

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, id: int) -> User:
        return self.db.query(User).filter(User.id == id).first()

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()
