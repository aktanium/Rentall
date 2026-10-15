from decimal import Decimal

import pytest

from app.utils import category_icon, format_price, plural_ru


@pytest.mark.parametrize(
    ("amount", "unit", "expected"),
    [
        (Decimal("150"), "hour", "150 сом / час"),
        (Decimal("2500.00"), "day", "2 500 сом / сутки"),
        (Decimal("12000"), "day", "12 000 сом / сутки"),
        (Decimal("1250000"), "day", "1 250 000 сом / сутки"),
        (Decimal("99.50"), "hour", "99,50 сом / час"),
        (2500, None, "2 500 сом"),
    ],
)
def test_format_price(amount, unit, expected):
    assert format_price(amount, unit) == expected


def test_price_filter_is_registered(app):
    template = app.jinja_env.from_string("{{ price|price('hour') }}")
    assert template.render(price=Decimal("150")) == "150 сом / час"


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (0, "отзывов"),
        (1, "отзыв"),
        (2, "отзыва"),
        (5, "отзывов"),
        (11, "отзывов"),
        (21, "отзыв"),
        (22, "отзыва"),
        (112, "отзывов"),
    ],
)
def test_plural_ru(n, expected):
    assert plural_ru(n, "отзыв", "отзыва", "отзывов") == expected


def test_category_icon():
    assert category_icon("cars") == "bi-car-front-fill"
    assert category_icon("unknown") == "bi-grid-fill"
