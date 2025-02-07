from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.client import Base
from sqlalchemy import func
import uuid
from app.utils.functions import generate_referral_code
from sqlalchemy.dialects.postgresql import JSONB


class Referral(Base):
    __tablename__ = "referrals"
    id = Column(String, index=True, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(String, ForeignKey("users.id"), nullable=True, unique=True)
    owner = relationship("User", back_populates="referral")
    referral_code = Column(
        String, index=True, default=generate_referral_code, unique=True
    )
    referred_user_ids = Column(JSONB, default=list)

    def __repr__(self):
        return f"<Referral(id={self.id}, created_at={self.created_at}, total_used={self.total_used}), referral_code={self.referral_code}>"

    @property
    def total_used(self):
        return len(self.referred_user_ids) if self.referred_user_ids else 0
