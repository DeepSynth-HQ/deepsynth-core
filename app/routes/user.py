from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers.user import UserController
from app.dto import UserRequestDTO, UserResponseDTO
from app.database.client import get_db
from log import logger

router = APIRouter(tags=["user"])


@router.post("/users")
def create_user(user: UserRequestDTO, db: Session = Depends(get_db)) -> UserResponseDTO:
    user_controller = UserController(db)
    user_response = user_controller.create_user(user)
    logger.info(f"User created: {user_response}")
    return UserResponseDTO(
        id=user_response.id,
        email=user_response.email,
        username=user_response.username,
        created_at=user_response.created_at,
        updated_at=user_response.updated_at,
    )
