from fastapi import APIRouter

from app.api.v1.routes import auth, health, me, products

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(products.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(me.router)
