"""Demo data for local development and live demos. Safe to run many times."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select

from app.extensions import db
from app.models import Category, Listing, ListingImage, User

SEED_PASSWORD = "password123"
CITY = "Бишкек"
IMAGES_PER_LISTING = 2

CATEGORIES = [
    # (slug, name, default_price_unit)
    ("cars", "Машины", "day"),
    ("bikes", "Велосипеды", "hour"),
    ("scooters", "Самокаты", "hour"),
    ("housing", "Жильё", "day"),
    ("venues", "Площадки", "hour"),
]

USERS = [
    # (email, name, phone, is_owner)
    ("azamat@example.com", "Азамат Токтогулов", "+996 555 100 101", True),
    ("aigerim@example.com", "Айгерим Садыкова", "+996 700 200 202", True),
    ("bekzat@example.com", "Бекзат Алиев", "+996 772 300 303", False),
    ("nurlan@example.com", "Нурлан Касымов", "+996 555 400 404", False),
    ("elvira@example.com", "Эльвира Мамбетова", "+996 709 500 505", False),
]

# (owner email, category slug, title, description, price KGS, unit, address, lat, lng)
LISTINGS = [
    (
        "azamat@example.com",
        "cars",
        "Toyota Camry 70, 2019",
        "Автомат, кондиционер, бензин. Чистый салон, страховка включена.",
        "3500",
        "day",
        "ул. Киевская, 96",
        42.8761,
        74.5962,
    ),
    (
        "azamat@example.com",
        "cars",
        "Honda Fit, 2015",
        "Экономичный городской автомобиль, гибрид. Идеально для поездок по городу.",
        "2000",
        "day",
        "пр. Манаса, 40",
        42.8652,
        74.5871,
    ),
    (
        "aigerim@example.com",
        "cars",
        "Lexus RX 350, 2018",
        "Полный привод, кожаный салон. Подходит для поездок на Иссык-Куль.",
        "6000",
        "day",
        "ул. Токтогула, 125",
        42.8703,
        74.6004,
    ),
    (
        "aigerim@example.com",
        "cars",
        "Hyundai Sonata, 2020",
        "Газ/бензин, камера заднего вида, Apple CarPlay.",
        "3000",
        "day",
        "пр. Чуй, 190",
        42.8772,
        74.6151,
    ),
    (
        "azamat@example.com",
        "bikes",
        "Горный велосипед Merida Big Nine",
        'Рама 19", 29" колёса, гидравлические тормоза. Шлем в подарок.',
        "150",
        "hour",
        "ул. Ахунбаева, 119",
        42.8421,
        74.6043,
    ),
    (
        "azamat@example.com",
        "bikes",
        "Городской велосипед Stels Navigator",
        "Удобная посадка, корзина и багажник. Для прогулок по паркам.",
        "100",
        "hour",
        "ул. Исанова, 42",
        42.8789,
        74.6031,
    ),
    (
        "aigerim@example.com",
        "bikes",
        "Шоссейный велосипед Giant Contend",
        "Лёгкая алюминиевая рама, 18 скоростей. Для длинных поездок за город.",
        "1200",
        "day",
        "мкр Джал, ул. Байтик Баатыра, 2",
        42.8331,
        74.5852,
    ),
    (
        "aigerim@example.com",
        "bikes",
        'Детский велосипед Forward 20"',
        "Для детей 6–10 лет, есть боковые колёса.",
        "80",
        "hour",
        "парк Ататюрка, ул. Ахунбаева",
        42.8436,
        74.5948,
    ),
    (
        "azamat@example.com",
        "scooters",
        "Электросамокат Xiaomi Mi 4 Pro",
        "Запас хода до 45 км, максимальная скорость 25 км/ч.",
        "200",
        "hour",
        "ул. Московская, 172",
        42.8706,
        74.6042,
    ),
    (
        "azamat@example.com",
        "scooters",
        "Электросамокат Ninebot Max G30",
        'Запас хода до 65 км, надувные колёса 10". Зарядка в комплекте.',
        "250",
        "hour",
        "ул. Боконбаева, 120",
        42.8681,
        74.6052,
    ),
    (
        "aigerim@example.com",
        "scooters",
        "Электросамокат Kugoo M4",
        "Сиденье, амортизаторы, подходит для неровных дорог.",
        "180",
        "hour",
        "пр. Жибек Жолу, 500",
        42.8898,
        74.6153,
    ),
    (
        "aigerim@example.com",
        "scooters",
        "Самокат на весь день Kugoo S3",
        "Лёгкий складной самокат, удобно брать в маршрутку.",
        "900",
        "day",
        "ул. Горького, 1",
        42.8581,
        74.6102,
    ),
    (
        "azamat@example.com",
        "housing",
        "1-комнатная квартира в центре",
        "Рядом с площадью Ала-Тоо. Wi-Fi, стиральная машина, кухня.",
        "2500",
        "day",
        "ул. Панфилова, 120",
        42.8745,
        74.5915,
    ),
    (
        "azamat@example.com",
        "housing",
        "2-комнатная квартира в Асанбае",
        "Новостройка, 9 этаж, вид на горы. До 4 гостей.",
        "3500",
        "day",
        "мкр Асанбай, 45",
        42.8205,
        74.6248,
    ),
    (
        "aigerim@example.com",
        "housing",
        "Студия в мкр Джал",
        "Уютная студия для одного-двух человек, рядом супермаркет.",
        "2000",
        "day",
        "мкр Джал-29, 12",
        42.8298,
        74.5781,
    ),
    (
        "aigerim@example.com",
        "housing",
        "Коттедж с бассейном",
        "Дом на 10 гостей, бассейн, сауна, мангальная зона.",
        "12000",
        "day",
        "Южная магистраль, 88",
        42.8272,
        74.6003,
    ),
    (
        "azamat@example.com",
        "venues",
        "Лофт для фотосессий и вечеринок",
        "150 м², панорамные окна, звук и свет. До 40 человек.",
        "2500",
        "hour",
        "ул. Логвиненко, 8",
        42.8792,
        74.5934,
    ),
    (
        "azamat@example.com",
        "venues",
        "Банкетный зал «Ала-Тоо»",
        "Зал на 150 гостей, сцена, кухня и обслуживание.",
        "8000",
        "hour",
        "пр. Чуй, 253",
        42.8763,
        74.6213,
    ),
    (
        "aigerim@example.com",
        "venues",
        "Конференц-зал в бизнес-центре",
        "30 мест, проектор, флипчарт, кофе-брейк по запросу.",
        "3000",
        "hour",
        "ул. Ибраимова, 115",
        42.8758,
        74.6139,
    ),
    (
        "aigerim@example.com",
        "venues",
        "Летняя терраса у Ботанического сада",
        "Открытая площадка до 60 человек, гирлянды и мебель включены.",
        "4000",
        "hour",
        "ул. Ахунбаева, 1а",
        42.8432,
        74.6251,
    ),
]


@dataclass
class SeedResult:
    categories: int = 0
    users: int = 0
    listings: int = 0


def seed() -> SeedResult:
    """Create demo categories, users and listings that don't exist yet."""
    result = SeedResult()

    categories = {}
    for slug, name, unit in CATEGORIES:
        category = db.session.scalar(select(Category).where(Category.slug == slug))
        if category is None:
            category = Category(slug=slug, name=name, default_price_unit=unit)
            db.session.add(category)
            result.categories += 1
        categories[slug] = category

    users = {}
    for email, name, phone, is_owner in USERS:
        user = db.session.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, name=name, phone=phone, is_owner=is_owner)
            user.set_password(SEED_PASSWORD)
            db.session.add(user)
            result.users += 1
        users[email] = user

    db.session.flush()

    for index, (owner_email, slug, title, description, price, unit, address, lat, lng) in enumerate(
        LISTINGS, start=1
    ):
        owner = users[owner_email]
        exists = db.session.scalar(
            select(Listing.id).where(Listing.owner_id == owner.id, Listing.title == title)
        )
        if exists:
            continue
        listing = Listing(
            owner=owner,
            category=categories[slug],
            title=title,
            description=description,
            price=Decimal(price),
            price_unit=unit,
            city=CITY,
            address=address,
            lat=lat,
            lng=lng,
        )
        listing.images = [
            ListingImage(
                url=f"https://picsum.photos/seed/rentall-{index}-{pos}/800/600", position=pos
            )
            for pos in range(IMAGES_PER_LISTING)
        ]
        db.session.add(listing)
        result.listings += 1

    db.session.commit()
    return result
