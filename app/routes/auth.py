from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dto import LoginRequest, SignupRequest, SocialCallbackRequest
from app.controllers.auth import AuthController
from app.database import get_db
from fastapi.responses import RedirectResponse
from config import settings
from app.dto import LoginXRequest
from fastapi import HTTPException

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.get("/x")
async def x_login(db: Session = Depends(get_db)):
    auth_controller = AuthController(db)
    x_auth_url = auth_controller.auth_x()

    return RedirectResponse(url=x_auth_url)


@router.get("/callback/x")
async def x_callback(code: str, state: str, db: Session = Depends(get_db)):
    auth_controller = AuthController(db)
    try:
        url = auth_controller.callback_x(code, state)
        return RedirectResponse(url=url)
    except Exception as e:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error={str(e)}")


@router.post("/login/x")
async def login_x(request: LoginXRequest, db: Session = Depends(get_db)):
    """Handle direct X token login"""
    auth_controller = AuthController(db)
    try:
        result = auth_controller.login_x(request.token)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
