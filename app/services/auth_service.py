from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, new_session_token, verify_password
from app.models.user import User, UserRole
from app.repositories import session_repository, user_repository


class AuthError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


async def register_client(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    full_name: str,
) -> User:
    existing = await user_repository.get_user_by_email(db, email)
    if existing is not None:
        raise AuthError("email_taken", "E-mail já cadastrado")
    pw_hash = hash_password(password)
    user = await user_repository.create_user(
        db,
        email=email,
        password_hash=pw_hash,
        full_name=full_name,
        role=UserRole.client,
    )
    return user


async def login(
    db: AsyncSession,
    *,
    email: str,
    password: str,
) -> tuple[User, str, str]:
    user = await user_repository.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("invalid_credentials", "E-mail ou senha inválidos")
    raw = new_session_token()
    sess = await session_repository.create_session(db, user_id=user.id, raw_token=raw)
    return user, str(sess.id), raw
