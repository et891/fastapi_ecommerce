from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Product, Review
from app.schemas import Product as ProductSchema, ProductCreate, Review as ReviewSchema
from sqlalchemy.orm import Session
from app.db_depends import get_db, get_async_db
from app.models.users import User as UserModel
from app.auth import get_current_seller

# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema],status_code=status.HTTP_200_OK)
async def get_all_products(db: Annotated[AsyncSession, Depends(get_async_db)]):
    """
    Возвращает список всех товаров.
    """
    stmt = select(Product).where(Product.is_active == True)
    products = await db.execute(stmt)
    products = products.scalars().all()
    return products


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    category_result = await db.scalars(
        select(Category).where(Category.id == product.category_id, Category.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    db_product = Product(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)  # Для получения id и is_active из базы
    return db_product


@router.get("/category/{category_id}",response_model=list[ProductSchema],status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt = select(Category).where(Category.id == category_id,
                                    Category.is_active == True)
    r = await db.execute(stmt)
    r = r.scalar()
    if r is None:
        raise HTTPException(status_code=400, detail="Category not found")

    stmt = select(Product).where(Product.category_id == category_id, Product.is_active == True)
    result = await db.execute(stmt)
    result = result.scalars().all()

    return result


@router.get("/{product_id}",response_model=ProductSchema,status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]):
    """
    Возвращает детальную информацию о товаре по его ID.
    """

    stmt = select(Product).where(Product.id == product_id, Product.is_active == True)
    result = await db.scalars(stmt)
    result = result.first()
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    r = await db.scalar(select(Category).where(Category.id == result.category_id, Category.is_active == True))
    if r is None:
        raise HTTPException(status_code=400, detail="Category not found")
    return result

@router.get("/{product_id}/reviews/", response_model=list[ReviewSchema])
async def get_reviews_by_product_id(product_id: int, db :AsyncSession = Depends(get_async_db)):
    """
    Получение отзывов о конкретном товаре
    """
    stmt = select(Product).where(Product.id == product_id, Product.is_active == True)
    product = await db.scalar(stmt)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    stmt1 = select(Review).where(
        Review.product_id == product_id,
        Review.is_active.is_(True),
    )
    reviews = await db.scalars(stmt1)
    return reviews.all()


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(select(Product).where(Product.id == product_id))
    db_product = result.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    category_result = await db.scalars(
        select(Category).where(Category.id == product.category_id, Category.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    await db.execute(
        update(Product).where(Product.id == product_id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)  # Для консистентности данных
    return db_product


@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
    await db.execute(
        update(Product).where(Product.id == product_id).values(is_active=False)
    )
    await db.commit()
    await db.refresh(product)  # Для возврата is_active = False
    return product