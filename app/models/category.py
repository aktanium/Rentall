from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

PRICE_UNITS = ("hour", "day")


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("default_price_unit IN ('hour', 'day')", name="default_price_unit_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    default_price_unit: Mapped[str] = mapped_column(String(4))

    listings: Mapped[list["Listing"]] = relationship(back_populates="category")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Category {self.slug}>"
