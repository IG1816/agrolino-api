import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel

from app.models.product import ProductCategory, ProductStatus


class ProductPublicOut(BaseModel):
    """Resposta pública de produto; JSON em camelCase (alias_generator)."""

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    id: uuid.UUID
    sku: str
    slug: str
    category: ProductCategory
    name: str
    description: str
    image_url: str | None
    price_cents: int
    promo_price_cents: int | None
    promo_ends_at: datetime | None
    stock_qty: int
    unit: str
    status: ProductStatus
    sort_order: int
    is_featured: bool

    @computed_field
    @property
    def promo_active(self) -> bool:
        if self.promo_price_cents is None:
            return False
        if self.promo_ends_at is not None and self.promo_ends_at.astimezone(UTC) < datetime.now(UTC):
            return False
        return True

    @computed_field
    @property
    def promo_discount_percent(self) -> int | None:
        if not self.promo_active or self.promo_price_cents is None or self.price_cents <= 0:
            return None
        return int(round((1 - (self.promo_price_cents / self.price_cents)) * 100))


class ProductListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[ProductPublicOut]
    total: int
    page: int
    page_size: int
