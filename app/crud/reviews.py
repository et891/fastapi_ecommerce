from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.models import Product
from app.models.reviews import Review


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(Review.grade)).where(
            Review.product_id == product_id,
            Review.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(Product, product_id)
    product.rating = avg_rating
    # await db.commit()








