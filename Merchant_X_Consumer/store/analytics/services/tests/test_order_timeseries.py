import pytest
from datetime import date, datetime
from decimal import Decimal

from store.analytics.services.order_analytics import build_order_timeseries
from store.models import Order
from tests.factories.order_factory import OrderFactory, OrderItemFactory
from tests.factories.user_factory import MerchantFactory, MemberFactory
from tests.factories.product_factory import ProductFactory


@pytest.mark.django_db
def test_timeseries_day_basic_with_zero_fill():
    """
    day 分組：
    - 有訂單的日子要有正確 GMV / order_count
    - 沒有訂單的日子要補 0
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("100.00"))

    # 1/10 有一筆訂單
    order = OrderFactory(
        member=member,
        status=Order.StatusChoices.PAID,
        set_created_at=datetime(2026, 1, 10, 10, 0),
    )
    OrderItemFactory(order=order, product=product, quantity=2)  # 200

    series = build_order_timeseries(
        merchant=merchant,
        start=date(2026, 1, 9),
        end=date(2026, 1, 11),
        group_by="day",
    )

    assert len(series) == 3

    assert series[0]["date"] == date(2026, 1, 9)
    assert series[0]["order_count"] == 0
    assert series[0]["gmv"] == Decimal("0.00")

    assert series[1]["date"] == date(2026, 1, 10)
    assert series[1]["order_count"] == 1
    assert series[1]["gmv"] == Decimal("200.00")

    assert series[2]["date"] == date(2026, 1, 11)
    assert series[2]["order_count"] == 0
    assert series[2]["gmv"] == Decimal("0.00")


@pytest.mark.django_db
def test_timeseries_order_count_is_distinct_per_day():
    """
    同一天、一筆訂單、多個 OrderItem
    → order_count 仍然只能是 1
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("50.00"))

    order = OrderFactory(
        member=member,
        status=Order.StatusChoices.PAID,
        set_created_at=datetime(2026, 1, 5, 12, 0),
    )

    OrderItemFactory(order=order, product=product, quantity=1)
    OrderItemFactory(order=order, product=product, quantity=3)

    series = build_order_timeseries(
        merchant=merchant,
        start=date(2026, 1, 5),
        end=date(2026, 1, 5),
        group_by="day",
    )

    assert len(series) == 1
    row = series[0]

    assert row["order_count"] == 1
    assert row["gmv"] == Decimal("200.00")  # 50 * (1 + 3)


@pytest.mark.django_db
def test_timeseries_status_filter_is_applied():
    """
    status 篩選必須生效（例如只算 PAID）
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("100.00"))

    # PAID
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=datetime(2026, 1, 10),
        ),
        product=product,
        quantity=1,
    )

    # CANCELED
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.CANCELED,
            set_created_at=datetime(2026, 1, 10),
        ),
        product=product,
        quantity=5,
    )

    series = build_order_timeseries(
        merchant=merchant,
        start=date(2026, 1, 10),
        end=date(2026, 1, 10),
        group_by="day",
        statuses=[Order.StatusChoices.PAID],
    )

    row = series[0]
    assert row["order_count"] == 1
    assert row["gmv"] == Decimal("100.00")


@pytest.mark.django_db
def test_timeseries_month_grouping():
    """
    month 分組：
    - 同月資料要彙總
    - date 一律回該月第一天
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("30.00"))

    # 1 月兩筆訂單
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=datetime(2026, 1, 5),
        ),
        product=product,
        quantity=1,
    )
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=datetime(2026, 1, 20),
        ),
        product=product,
        quantity=2,
    )

    # 2 月一筆訂單
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=datetime(2026, 2, 3),
        ),
        product=product,
        quantity=3,
    )

    series = build_order_timeseries(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 2, 28),
        group_by="month",
    )

    assert len(series) == 2

    jan = series[0]
    assert jan["date"] == date(2026, 1, 1)
    assert jan["order_count"] == 2
    assert jan["gmv"] == Decimal("90.00")  # 30 * (1 + 2)

    feb = series[1]
    assert feb["date"] == date(2026, 2, 1)
    assert feb["order_count"] == 1
    assert feb["gmv"] == Decimal("90.00")  # 30 * 3
