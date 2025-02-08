from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from config import settings
import jwt
from log import logger
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    try:
        token = credentials.credentials
        logger.info(f"Token: {token}")
        # Verify token
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        logger.info(f"Payload: {payload}")
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    except jwt.PyJWTError as e:
        import traceback

        traceback.print_exc()
        logger.error(f"Error decoding token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    finally:
        db.close()
