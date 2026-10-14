from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Listing(db.Model):
    __tablename__ = "listings"
    __table_args__ = (
        CheckConstraint("price > 0", name="price_positive"),
        CheckConstraint("price_unit IN ('hour', 'day')", name="price_unit_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    price_unit: Mapped[str] = mapped_column(String(4))
    city: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))
    lat: Mapped[float | None]
    lng: Mapped[float | None]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="listings")  # noqa: F821
    category: Mapped["Category"] = relationship(back_populates="listings")  # noqa: F821
    images: Mapped[list["ListingImage"]] = relationship(
        back_populates="listing",
        order_by="ListingImage.position",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="listing")  # noqa: F821
    reviews: Mapped[list["Review"]] = relationship(back_populates="listing")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Listing {self.id} {self.title!r}>"


class ListingImage(db.Model):
    __tablename__ = "listing_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(500))
    position: Mapped[int] = mapped_column(default=0, server_default="0")

    listing: Mapped["Listing"] = relationship(back_populates="images")
