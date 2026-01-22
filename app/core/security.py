from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt

# Workaround for passlib 1.7.4 + bcrypt 5.0.0 compatibility issue
# Patch bcrypt.hashpw to truncate passwords > 72 bytes before passlib imports it
try:
    import bcrypt
    original_hashpw = bcrypt.hashpw
    
    def patched_hashpw(secret, salt):
        # Truncate secret to 72 bytes if it's longer (bcrypt limit)
        if isinstance(secret, str):
            secret_bytes = secret.encode('utf-8')
        else:
            secret_bytes = secret
        if len(secret_bytes) > 72:
            secret_bytes = secret_bytes[:72]
            # Remove incomplete UTF-8 sequences
            while secret_bytes and secret_bytes[-1] & 0b11000000 == 0b10000000:
                secret_bytes = secret_bytes[:-1]
        return original_hashpw(secret_bytes, salt)
    
    bcrypt.hashpw = patched_hashpw
except (ImportError, AttributeError):
    # If patching fails, continue anyway
    pass

from passlib.context import CryptContext

from app.core.config import settings

# Configure CryptContext with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _truncate_password(password: str, max_bytes: int = 72) -> str:
    """Truncate password to max_bytes bytes, handling UTF-8 encoding properly."""
    encoded = password.encode('utf-8')
    if len(encoded) <= max_bytes:
        return password
    # Truncate to max_bytes bytes, ensuring we don't break UTF-8 sequences
    truncated_bytes = encoded[:max_bytes]
    # Remove any incomplete UTF-8 sequences at the end
    while truncated_bytes and truncated_bytes[-1] & 0b11000000 == 0b10000000:
        truncated_bytes = truncated_bytes[:-1]
    return truncated_bytes.decode('utf-8', errors='ignore')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt has a 72-byte limit, so truncate passwords longer than that
    truncated_password = _truncate_password(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    # bcrypt has a 72-byte limit, so truncate passwords longer than that
    truncated_password = _truncate_password(password)
    return pwd_context.hash(truncated_password)
