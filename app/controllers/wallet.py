from sqlalchemy.orm import Session
from app.services.wallet import WalletService
from app.dto import WalletRequestDTO, WalletResponseDTO


class WalletController:
    def __init__(self, db: Session):
        self.db = db
        self.wallet_service = WalletService(db)

    def generate_wallet(self):
        return self.wallet_service.generate_wallet()

    def create_wallet(self, wallet: WalletRequestDTO) -> WalletResponseDTO:
        wallet = self.wallet_service.create_wallet(wallet)
        return WalletResponseDTO.model_validate(wallet)
