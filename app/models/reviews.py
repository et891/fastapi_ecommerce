from datetime import datetime

from sqlalchemy import Boolean, Integer, Text, DateTime, CheckConstraint, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"
    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id : Mapped[int] = mapped_column(Integer , ForeignKey("users.id"))
    product_id : Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    comment: Mapped[str| None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now,server_default=func.now(), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    product : Mapped["Product"] = relationship("Product", back_populates="reviews")
    user : Mapped["User"] = relationship("User", back_populates="reviews")

    __table_args__ = (
        CheckConstraint('grade >= 1 AND grade <= 5', name='grade_range_check'),
    )



if __name__ == "__main__":
    from sqlalchemy.schema import CreateTable
    from app.models import User

    print(CreateTable(User.__table__))
    print(CreateTable(Review.__table__))
