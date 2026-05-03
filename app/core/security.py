import hashlib
import secrets
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, password_hash: str) -> bool:
    try:
        _ph.verify(password_hash, plain)
        return True
    except VerifyMismatchError:
        return False


def new_session_token() -> str:
    """Token opaco enviado no cookie (não colocar dados sensíveis no valor)."""
    return secrets.token_urlsafe(32)


def session_cookie_value(session_id: UUID, token: str) -> str:
    """Formato interno do cookie: id.token (validação no servidor)."""
    return f"{session_id.hex}.{token}"


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
