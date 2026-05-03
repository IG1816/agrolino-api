from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import parse_session_cookie
from app.core.config import settings
from app.core.constants import SESSION_COOKIE_NAME
from app.core.security import session_cookie_value
from app.db.session import get_db
from app.repositories import session_repository
from app.schemas.auth import LoginIn, MessageOut, RegisterIn
from app.services.auth_service import AuthError, login as login_user
from app.services.auth_service import register_client

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, *, session_id: UUID, raw_token: str) -> None:
    value = session_cookie_value(session_id, raw_token)
    max_age = settings.session_ttl_hours * 3600
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=value,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=max_age,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


@router.post("/register", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_db)) -> MessageOut:
    try:
        await register_client(
            db,
            email=str(body.email),
            password=body.password,
            full_name=body.full_name,
        )
        await db.commit()
    except AuthError as e:
        await db.rollback()
        if e.code == "email_taken":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message) from e
        raise
    return MessageOut(message="Conta criada com sucesso.")


@router.post("/login", response_model=MessageOut)
async def login(body: LoginIn, response: Response, db: AsyncSession = Depends(get_db)) -> MessageOut:
    try:
        _user, session_id, raw_token = await login_user(
            db,
            email=str(body.email),
            password=body.password,
        )
        await db.commit()
    except AuthError as e:
        await db.rollback()
        if e.code == "invalid_credentials":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message) from e
        raise
    _set_session_cookie(response, session_id=session_id, raw_token=raw_token)
    return MessageOut(message="Sessão iniciada.")


@router.post("/logout", response_model=MessageOut)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> MessageOut:
    raw = request.cookies.get(SESSION_COOKIE_NAME)
    parsed = parse_session_cookie(raw)
    if parsed is not None:
        session_id, token = parsed
        sess = await session_repository.get_valid_session(db, session_id=session_id, raw_token=token)
        if sess is not None:
            await session_repository.delete_session(db, session_id=sess.id)
        await db.commit()
    _clear_session_cookie(response)
    return MessageOut(message="Sessão encerrada.")
