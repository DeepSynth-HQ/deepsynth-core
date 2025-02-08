import hashlib
import uuid
import jwt
from datetime import datetime, timedelta
from typing import Dict
from config import settings


def ref_generator(input_string):
    hash_object = hashlib.sha256(input_string.encode())
    full_hash = hash_object.hexdigest()
    short_hash = full_hash[:6]
    return short_hash


def generate_uuid():
    """Generate a UUID"""
    return str(uuid.uuid4())


def generate_referral_code():
    import random
    import string

    chars = "".join(c for c in string.ascii_letters + string.digits if c not in "01OIL")
    return "".join(random.choices(chars, k=8))


def generate_id():
    return str(uuid.uuid4())


def create_jwt_token(payload: Dict) -> str:
    """Create a JWT token with the given payload"""
    expiration = datetime.now() + timedelta(seconds=settings.JWT_EXPIRATION)
    payload["exp"] = expiration

    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_jwt_token(token: str) -> Dict:
    """Verify and decode a JWT token"""
    try:
        print("TOKEN", token)
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


if __name__ == "__main__":
    for _ in range(100):
        print(generate_referral_code())
