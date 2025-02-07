from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dto import UseRefCodeRequest
from app.controllers.referral import ReferralController
from app.database import get_db
from app.middleware.auth import verify_token
from app.models.user import User

router = APIRouter(tags=["referral"])


@router.post("/ref/use")
def use_ref(
    body: UseRefCodeRequest,
    user: User = Depends(verify_token),
    db: Session = Depends(get_db),
):
    ref_controller = ReferralController(db)
    return ref_controller.use_ref(body, user)
