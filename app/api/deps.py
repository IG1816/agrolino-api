from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SESSION_COOKIE_NAME
from app.db.session import get_db
from app.models.user import User
from app.repositories import session_repository


def parse_session_cookie(raw: str | None) -> tuple[UUID, str] | None:
    if not raw or "." not in raw:
        return None
    sid_hex, token = raw.split(".", 1)
    if len(sid_hex) != 32:
        return None
    try:
        return UUID(hex=sid_hex), token
    except ValueError:
        return None


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    session_cookie: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> User:
    parsed = parse_session_cookie(session_cookie)
    if parsed is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    session_id, token = parsed
    sess = await session_repository.get_valid_session(db, session_id=session_id, raw_token=token)
    if sess is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida ou expirada")
    user = await db.get(User, sess.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    from app.models.user import UserRole

    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrador necessário")
    return user
