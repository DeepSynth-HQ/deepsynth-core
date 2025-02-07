from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dto import LoginRequest, SignupRequest, SocialCallbackRequest
from app.controllers.auth import AuthController
from app.database import get_db

router = APIRouter(tags=["auth"])


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    auth_controller = AuthController(db)
    return auth_controller.login(body)


@router.post("/signup")
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    auth_controller = AuthController(db)
    return auth_controller.signup(body)


@router.post("/callback/social")
def callback_social(body: SocialCallbackRequest, db: Session = Depends(get_db)):
    auth_controller = AuthController(db)
    return auth_controller.callback_social(body)
