from fastapi import APIRouter, Request, Depends
from app.controllers.wallet import WalletController
from app.middleware.decorator import rate_limit
from config import settings
from app.dto import WalletRequestDTO
from app.database.client import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["wallet"])


@router.post("/wallet/generate")
@rate_limit(
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS + 100,
    window=settings.RATE_LIMIT_WINDOW,
)
def generate_wallet(request: Request, db: Session = Depends(get_db)):
    return WalletController(db).generate_wallet()


@router.post("/wallet/create")
def create_wallet(wallet: WalletRequestDTO, db: Session = Depends(get_db)):
    return WalletController(db).create_wallet(wallet)
