from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Agrolino API",
        version="0.1.0",
        lifespan=lifespan,
        root_path="",
        # Atrás do proxy só em /api — documentação e OpenAPI no mesmo prefixo.
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.include_router(api_v1_router, prefix="/api/v1")
    return app


app = create_app()
