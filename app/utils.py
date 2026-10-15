from decimal import ROUND_HALF_UP, Decimal

PRICE_UNIT_LABELS = {"hour": "час", "day": "сутки"}

# Bootstrap Icons class per category slug.
CATEGORY_ICONS = {
    "cars": "bi-car-front-fill",
    "bikes": "bi-bicycle",
    "scooters": "bi-scooter",
    "housing": "bi-house-door-fill",
    "venues": "bi-balloon-fill",
}
DEFAULT_CATEGORY_ICON = "bi-grid-fill"


def format_price(amount: Decimal | int | float, unit: str | None = None) -> str:
    """Format a price in KGS: 2500 -> "2 500 сом", with unit "day" -> "2 500 сом / сутки"."""
    amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    whole, cents = divmod(abs(amount), 1)
    text = f"{int(whole):,}".replace(",", " ")
    if cents:
        text += "," + f"{cents:.2f}"[2:]
    if amount < 0:
        text = "-" + text
    text += " сом"
    if unit:
        text += f" / {PRICE_UNIT_LABELS[unit]}"
    return text


def category_icon(slug: str) -> str:
    return CATEGORY_ICONS.get(slug, DEFAULT_CATEGORY_ICON)


def plural_ru(n: int, one: str, few: str, many: str) -> str:
    """Russian plural form: 1 отзыв, 2 отзыва, 5 отзывов."""
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def register_template_filters(app) -> None:
    app.add_template_filter(format_price, "price")
    app.add_template_filter(category_icon, "category_icon")
    app.add_template_filter(plural_ru, "plural_ru")
