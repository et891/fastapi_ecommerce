from typing import Optional

from sqlalchemy import Boolean, String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base, engine


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str|None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[int|None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")  # New

    parent: Mapped[Optional["Category"]] = relationship("Category",
                                                        back_populates="children",
                                                        remote_side="Category.id")
    children: Mapped[list["Category"]] = relationship("Category",
                                                      back_populates="parent")



if __name__ == "__main__":
    from sqlalchemy.schema import CreateTable
    from app.models.products import Product
    print(CreateTable(Category.__table__))
    print(CreateTable(Product.__table__))
