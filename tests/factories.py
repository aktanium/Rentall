from decimal import Decimal

from app.extensions import db
from app.models import Category, Listing, ListingImage, User


def make_user(email: str, *, is_owner: bool = False, name: str = "Test User") -> User:
    user = User(email=email, name=name, is_owner=is_owner)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def make_category(slug: str = "cars", name: str = "Машины", unit: str = "day") -> Category:
    category = Category(slug=slug, name=name, default_price_unit=unit)
    db.session.add(category)
    db.session.commit()
    return category


def make_listing(
    owner: User,
    category: Category,
    title: str = "Toyota Camry",
    *,
    price: str = "3500",
    price_unit: str = "day",
    is_active: bool = True,
    images: int = 1,
    lat: float | None = 42.8761,
    lng: float | None = 74.5962,
) -> Listing:
    listing = Listing(
        owner=owner,
        category=category,
        title=title,
        description="Описание объявления",
        price=Decimal(price),
        price_unit=price_unit,
        city="Бишкек",
        address="ул. Киевская, 96",
        lat=lat,
        lng=lng,
        is_active=is_active,
        images=[
            ListingImage(url=f"https://picsum.photos/seed/{title}-{i}/800/600", position=i)
            for i in range(images)
        ],
    )
    db.session.add(listing)
    db.session.commit()
    return listing


def login(client, email: str, password: str = "password123", **extra):
    return client.post("/auth/login", data={"email": email, "password": password, **extra})
