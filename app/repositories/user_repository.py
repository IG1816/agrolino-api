from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    r = await db.execute(select(User).where(User.email == email.lower()))
    return r.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    password_hash: str,
    full_name: str,
    role: UserRole = UserRole.client,
) -> User:
    user = User(
        email=email.lower(),
        password_hash=password_hash,
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    r = await db.execute(select(User).where(User.id == user_id))
    return r.scalar_one_or_none()


async def patch_user(
    db: AsyncSession,
    user: User,
    *,
    full_name: str | None = None,
    phone: str | None = None,
    address_line: str | None = None,
    city: str | None = None,
    state: str | None = None,
) -> User:
    if full_name is not None:
        user.full_name = full_name
    if phone is not None:
        user.phone = phone
    if address_line is not None:
        user.address_line = address_line
    if city is not None:
        user.city = city
    if state is not None:
        user.state = state.upper() if state else None
    await db.flush()
    return user
