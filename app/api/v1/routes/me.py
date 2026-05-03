from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserMeOut, UserMePatch

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserMeOut)
async def read_me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("", response_model=UserMeOut)
async def update_me(
    body: UserMePatch,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> User:
    await user_repository.patch_user(
        db,
        user,
        full_name=body.full_name,
        phone=body.phone,
        address_line=body.address_line,
        city=body.city,
        state=body.state,
    )
    await db.commit()
    await db.refresh(user)
    return user
