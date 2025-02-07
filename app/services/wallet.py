from config import settings
import requests
from app.dto import WalletRequestDTO, WalletResponseDTO
from app.models.wallet import Wallet
from sqlalchemy.orm import Session


class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.base_url = settings.WALLET_API_URL
        self.headers = {"Content-Type": "application/json"}

    def generate_wallet(self):
        """
        Generate a new wallet in Solana
        """
        response = requests.post(
            f"{self.base_url}/api/wallet/generate", headers=self.headers
        )
        data = response.json()
        data = data["data"]
        data = {
            "seed_phrase": data["seedPhrase"],
            "private_key": data["privateKeyBase58"],
            "public_key": data["publicKey"],
        }
        return data

    def create_wallet(self, user_id: str) -> Wallet:
        created_wallet = self.generate_wallet()
        wallet_model = Wallet(**created_wallet, user_id=user_id)
        self.db.add(wallet_model)
        # self.db.commit()
        return wallet_model

    def get_wallet_by_user_id(self, user_id: str) -> Wallet:
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        return wallet if wallet else None
