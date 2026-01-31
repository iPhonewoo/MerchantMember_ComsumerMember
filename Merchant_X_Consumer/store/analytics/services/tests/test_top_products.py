import pytest
from datetime import date, datetime
from decimal import Decimal

from store.analytics.services.order_analytics import build_top_products
from store.models import Order
from tests.factories.order_factory import OrderFactory, OrderItemFactory
from tests.factories.user_factory import MerchantFactory, MemberFactory
from tests.factories.product_factory import ProductFactory


@pytest.mark.django_db
def test_build_top_products_basic_quantity_and_revenue():
    """
    基本熱門商品分析：
    - 商品 A：賣出 3 件（2 + 1），營收 300
    - 商品 B：賣出 1 件，營收 50
    - 依 quantity 排序
    """

    merchant = MerchantFactory()
    store = merchant.store

    member = MemberFactory()

    product_a = ProductFactory(store=store, price=Decimal("100.00"))
    product_b = ProductFactory(store=store, price=Decimal("50.00"))

    order1 = OrderFactory(
        member=member,
        status=Order.StatusChoices.PAID,
        set_created_at=datetime(2026, 1, 10),
    )
    order2 = OrderFactory(
        member=member,
        status=Order.StatusChoices.COMPLETED,
        set_created_at=datetime(2026, 1, 15),
    )

    # 商品 A：2 + 1
    OrderItemFactory(order=order1, product=product_a, quantity=2)
    OrderItemFactory(order=order2, product=product_a, quantity=1)

    # 商品 B：1
    OrderItemFactory(order=order2, product=product_b, quantity=1)

    results = build_top_products(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
        limit=10,
    )

    assert len(results) == 2
    assert results[0]["product_id"] == product_a.id
    assert results[0]["revenue"] >= results[1]["revenue"]

    first = results[0]
    assert first["product_id"] == product_a.id
    assert first["quantity"] == 3
    assert first["revenue"] == Decimal("300.00")
    assert first["order_count"] == 2

    second = results[1]
    assert second["product_id"] == product_b.id
    assert second["quantity"] == 1
    assert second["revenue"] == Decimal("50.00")
    assert second["order_count"] == 1


@pytest.mark.django_db
def test_order_count_is_distinct_for_product():
    """
    同一筆訂單中，同一商品出現多個 OrderItem
    → order_count 仍然只能算 1
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("40.00"))

    order = OrderFactory(
        member=member,
        status=Order.StatusChoices.PAID,
        set_created_at=datetime(2026, 1, 5),
    )

    OrderItemFactory(order=order, product=product, quantity=1)
    OrderItemFactory(order=order, product=product, quantity=2)

    results = build_top_products(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert len(results) == 1
    row = results[0]

    assert row["quantity"] == 3
    assert row["revenue"] == Decimal("120.00")
    assert row["order_count"] == 1


@pytest.mark.django_db
def test_canceled_orders_are_excluded_by_default():
    """
    canceled 訂單不應計入熱門商品分析
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
        quantity=2,
    )

    results = build_top_products(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert results == []


@pytest.mark.django_db
def test_limit_parameter_is_applied():
    """
    limit 參數必須生效
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("10.00"))

    for i in range(5):
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

    results = build_top_products(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
        limit=1,
    )

    assert len(results) == 1
