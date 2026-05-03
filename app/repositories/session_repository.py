from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_session_token
from app.models.user_session import UserSession


async def create_session(db: AsyncSession, *, user_id: UUID, raw_token: str) -> UserSession:
    th = hash_session_token(raw_token)
    expires = datetime.now(UTC) + timedelta(hours=settings.session_ttl_hours)
    row = UserSession(user_id=user_id, token_hash=th, expires_at=expires)
    db.add(row)
    await db.flush()
    return row


async def get_valid_session(db: AsyncSession, *, session_id: UUID, raw_token: str) -> UserSession | None:
    th = hash_session_token(raw_token)
    r = await db.execute(
        select(UserSession).where(
            UserSession.id == session_id,
            UserSession.token_hash == th,
            UserSession.expires_at > datetime.now(UTC),
        )
    )
    return r.scalar_one_or_none()


async def delete_session(db: AsyncSession, *, session_id: UUID) -> None:
    await db.execute(delete(UserSession).where(UserSession.id == session_id))
