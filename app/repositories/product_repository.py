from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductCategory, ProductStatus


async def count_public_products(
    db: AsyncSession,
    *,
    category: ProductCategory | None,
    featured: bool | None,
) -> int:
    q = select(func.count()).select_from(Product).where(Product.status != ProductStatus.hidden)
    if category is not None:
        q = q.where(Product.category == category)
    if featured is True:
        q = q.where(Product.is_featured.is_(True))
    r = await db.execute(q)
    return int(r.scalar_one())


async def list_public_products(
    db: AsyncSession,
    *,
    category: ProductCategory | None,
    featured: bool | None,
    page: int,
    page_size: int,
) -> list[Product]:
    q = select(Product).where(Product.status != ProductStatus.hidden)
    if category is not None:
        q = q.where(Product.category == category)
    if featured is True:
        q = q.where(Product.is_featured.is_(True))
    q = q.order_by(Product.sort_order.asc(), Product.name.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    r = await db.execute(q)
    return list(r.scalars().all())


async def get_product_by_slug(db: AsyncSession, slug: str) -> Product | None:
    r = await db.execute(select(Product).where(Product.slug == slug))
    return r.scalar_one_or_none()
