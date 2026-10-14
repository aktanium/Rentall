from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

BOOKING_STATUSES = ("pending", "confirmed", "paid", "completed", "cancelled")
# Bookings in these statuses block the dates (see the `no_overlap` EXCLUDE constraint).
ACTIVE_STATUSES = ("pending", "confirmed", "paid")


class Booking(db.Model):
    __tablename__ = "bookings"
    # The `no_overlap` EXCLUDE constraint is created in a separate migration
    # (add_bookings_no_overlap), since SQLAlchemy cannot autogenerate it.
    __table_args__ = (
        CheckConstraint("end_at > start_at", name="end_after_start"),
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'paid', 'completed', 'cancelled')",
            name="status_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    renter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(10), default="pending", server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    listing: Mapped["Listing"] = relationship(back_populates="bookings")  # noqa: F821
    renter: Mapped["User"] = relationship(back_populates="bookings")  # noqa: F821
    review: Mapped["Review | None"] = relationship(back_populates="booking")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Booking {self.id} {self.status}>"
