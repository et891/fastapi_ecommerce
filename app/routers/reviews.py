from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_buyer, get_current_admin
from app.crud.reviews import update_product_rating
from app.db_depends import get_async_db
from app.models.products import Product
from app.models.reviews import Review
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.models import User as UserModel

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

@router.get("/", response_model=list[ReviewSchema])
async def get_all_reviews(db :AsyncSession = Depends(get_async_db)):
    """
    Получение всех отзывов
    """
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    return reviews.all()


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(payload : ReviewCreate,
                        db :AsyncSession = Depends(get_async_db),
                        user: UserModel = Depends(get_current_buyer)
):
    """
    Добавление отзыва
    """
    stmt_1 = select(Product).where(Product.id == payload.product_id, Product.is_active == True)
    product = await db.scalar(stmt_1)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    stmt_2 = select(Review).where(Review.user_id == user.id, Review.product_id == product.id, Review.is_active == True)
    review = await db.scalar(stmt_2)
    if review is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You already reviewed this product")
    review = Review(**payload.model_dump(), user_id= user.id)
    db.add(review)
    await db.flush()
    await update_product_rating(db, product_id=product.id)
    await db.commit()
    await db.refresh(review)
    return review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: int,
                        db :AsyncSession = Depends(get_async_db),
                        admin: UserModel = Depends(get_current_admin)
):
    """
    Мягкое удаление отзыва
    """
    stmt = select(Review).where(Review.id == review_id, Review.is_active == True)
    review = await db.scalar(stmt)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    review.is_active = False
    await db.flush()
    await update_product_rating(db, product_id=review.product_id)
    await db.commit()
    return {"message": "Review deleted"}
