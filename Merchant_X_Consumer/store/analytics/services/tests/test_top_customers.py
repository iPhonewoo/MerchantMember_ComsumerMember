import pytest
from datetime import date, datetime
from decimal import Decimal

from store.analytics.services.order_analytics import build_top_customers
from store.models import Order
from tests.factories.order_factory import OrderFactory, OrderItemFactory
from tests.factories.user_factory import MerchantFactory, MemberFactory
from tests.factories.product_factory import ProductFactory


@pytest.mark.django_db
def test_build_top_customers_basic_gmv_and_order_count():
    """
    基本熟客分析：
    - Alice：2 筆訂單（各 1 個 OrderItem）
    - Bob：1 筆訂單
    - GMV 與 order_count 必須正確
    """

    merchant = MerchantFactory()
    store = merchant.store

    alice = MemberFactory(user__username="alice")
    bob = MemberFactory(user__username="bob")

    product_a = ProductFactory(store=store, price=Decimal("100.00"))
    product_b = ProductFactory(store=store, price=Decimal("50.00"))

    order1 = OrderFactory(
        member=alice,
        status=Order.StatusChoices.PAID,
        set_created_at=datetime(2026, 1, 10),
    )
    order2 = OrderFactory(
        member=alice,
        status=Order.StatusChoices.COMPLETED,
        set_created_at=datetime(2026, 1, 15),
    )
    order3 = OrderFactory(
        member=bob,
        status=Order.StatusChoices.PAID,
        set_created_at=datetime(2026, 1, 20),
    )

    OrderItemFactory(
        order=order1,
        product=product_a,
        quantity=2
    ) # 200.00
    OrderItemFactory(
        order=order2,
        product=product_b,
        quantity=1
    ) # 50.00
    OrderItemFactory(
        order=order3,
        product=product_b,
        quantity=3
    ) # 150.00

    results = build_top_customers(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
        limit=10,
    )

    assert len(results) == 2
    assert results[0]["total_gmv"] >= results[1]["total_gmv"]

    alice_row = results[0]
    assert alice_row["order__member__user__username"] == "alice"
    assert alice_row["order_count"] == 2
    assert alice_row["total_gmv"] == Decimal("250.00")

    bob_row = results[1]
    assert bob_row["order__member__user__username"] == "bob"
    assert bob_row["order_count"] == 1
    assert bob_row["total_gmv"] == Decimal("150.00")


@pytest.mark.django_db
def test_order_count_is_distinct_even_with_multiple_items():
    """
    一筆訂單有多個 OrderItem
    → order_count 必須仍然是 1（防 JOIN 放大）
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("30.00"))

    order = OrderFactory(
        member=member,
        status=Order.StatusChoices.PAID,
        set_created_at=datetime(2026, 1, 5),
    )

    OrderItemFactory(
        order=order,
        product=product,
        quantity=1,
    )
    OrderItemFactory(
        order=order,
        product=product,
        quantity=2,
    )

    results = build_top_customers(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
        limit=5,
    )

    assert len(results) == 1
    row = results[0]

    assert row["order_count"] == 1
    assert row["total_gmv"] == Decimal("90.00") # 30 * (1 + 2)


@pytest.mark.django_db
def test_canceled_orders_are_excluded_by_default():
    """
    canceled 訂單不應計入熟客分析
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("100.00"))

    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.CANCELED,
            set_created_at=datetime(2026, 1, 10),
        ),
        product=product,
        quantity=1,
    )

    results = build_top_customers(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert len(results) == 0


@pytest.mark.django_db
def test_limit_parameter_is_applied():
    """
    limit 參數必須生效
    """

    merchant = MerchantFactory()
    store = merchant.store

    product = ProductFactory(store=store, price=Decimal("10.00"))

    for i in range(10):
        member = MemberFactory(user__username=f"user{i}")
        order = OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=datetime(2026, 1, 10),
        )
        OrderItemFactory(
            order=order,
            product=product,
            quantity=i + 1,
        )

    results = build_top_customers(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
        limit=3,
    )

    assert len(results) == 3


@pytest.mark.django_db
def test_last_order_date_is_date_object():
    """
    last_order_date 必須是 date（不是 datetime）
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("20.00"))

    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=datetime(2026, 1, 12, 15, 30),
        ),
        product=product,
        quantity=1,
    )

    results = build_top_customers(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    row = results[0]
    assert isinstance(row["last_order_date"], date)
    assert row["last_order_date"] == date(2026, 1, 12)
