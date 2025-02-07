from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.services.user import UserService
from app.dto import UserRequestDTO, UserResponseDTO
from log import logger


class UserController:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def create_user(self, user: UserRequestDTO) -> User:
        try:
            return self.user_service.create_user(user)
        except IntegrityError as e:
            logger.error(f"Error creating user: {e}")
            raise e
