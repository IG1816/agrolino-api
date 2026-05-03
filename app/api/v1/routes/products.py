from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.product import ProductCategory, ProductStatus
from app.repositories import product_repository
from app.schemas.product import ProductListResponse, ProductPublicOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    category: ProductCategory | None = None,
    featured: bool | None = None,
) -> ProductListResponse:
    total = await product_repository.count_public_products(db, category=category, featured=featured)
    items = await product_repository.list_public_products(
        db, category=category, featured=featured, page=page, page_size=page_size
    )
    return ProductListResponse(
        items=[ProductPublicOut.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{slug}", response_model=ProductPublicOut)
async def get_product(slug: str, db: AsyncSession = Depends(get_db)) -> ProductPublicOut:
    p = await product_repository.get_product_by_slug(db, slug)
    if p is None or p.status == ProductStatus.hidden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return ProductPublicOut.model_validate(p)
