import pytest
from datetime import date, datetime
from decimal import Decimal

from store.analytics.services.order_analytics import build_order_summary
from store.models import Order
from tests.factories.order_factory import OrderFactory, OrderItemFactory
from tests.factories.user_factory import MerchantFactory, MemberFactory
from tests.factories.product_factory import ProductFactory


@pytest.mark.django_db
def test_order_summary_basic_metrics():
    """
    基本訂單總覽：
    - order_count
    - gmv
    - aov
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product_a = ProductFactory(store=store, price=Decimal("100.00"))
    product_b = ProductFactory(store=store, price=Decimal("50.00"))

    # 兩筆訂單
    order1 = OrderFactory(
        member=member,
        status=Order.StatusChoices.PAID,
        created_at=datetime(2026, 1, 10),
    )
    order2 = OrderFactory(
        member=member,
        status=Order.StatusChoices.COMPLETED,
        created_at=datetime(2026, 1, 15),
    )

    OrderItemFactory(order=order1, product=product_a, quantity=2)  # 200
    OrderItemFactory(order=order2, product=product_b, quantity=1)  # 50

    summary = build_order_summary(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert summary.order_count == 2
    assert summary.gmv == Decimal("250.00")
    assert summary.aov == Decimal("125.00")  # 250 / 2


@pytest.mark.django_db
def test_order_summary_excludes_orders_outside_date_range():
    """
    區間外的訂單不應被納入計算
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("100.00"))

    # 區間內
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=date(2026, 1, 10),
        ),
        product=product,
        quantity=1,
    )

    # 區間外
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=date(2025, 12, 31),
        ),
        product=product,
        quantity=10,
    )

    summary = build_order_summary(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert summary.order_count == 1
    assert summary.gmv == Decimal("100.00")


@pytest.mark.django_db
def test_order_summary_order_count_is_distinct():
    """
    同一筆訂單有多個 OrderItem
    → order_count 仍然只能算 1
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

    OrderItemFactory(order=order, product=product, quantity=1)
    OrderItemFactory(order=order, product=product, quantity=2)

    summary = build_order_summary(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert summary.order_count == 1
    assert summary.gmv == Decimal("90.00")  # 30 * (1 + 2)
    assert summary.aov == Decimal("90.00")


@pytest.mark.django_db
def test_order_summary_status_breakdown():
    """
    status_breakdown 應正確統計各狀態的訂單數
    """

    merchant = MerchantFactory()
    store = merchant.store
    member = MemberFactory()

    product = ProductFactory(store=store, price=Decimal("100.00"))

    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.PAID,
            set_created_at=datetime(2026, 1, 10),
        ),
        product=product,
        quantity=1,
    )
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.COMPLETED,
            set_created_at=datetime(2026, 1, 11),
        ),
        product=product,
        quantity=1,
    )
    OrderItemFactory(
        order=OrderFactory(
            member=member,
            status=Order.StatusChoices.CANCELED,
            set_created_at=datetime(2026, 1, 12),
        ),
        product=product,
        quantity=1,
    )

    summary = build_order_summary(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    breakdown = {row["status"]: row["count"] for row in summary.status_breakdown}

    assert breakdown[Order.StatusChoices.PAID] == 1
    assert breakdown[Order.StatusChoices.COMPLETED] == 1
    assert breakdown[Order.StatusChoices.CANCELED] == 1


@pytest.mark.django_db
def test_order_summary_zero_orders():
    """
    沒有任何訂單時：
    - order_count = 0
    - gmv = 0
    - aov = 0
    """

    merchant = MerchantFactory()

    summary = build_order_summary(
        merchant=merchant,
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
    )

    assert summary.order_count == 0
    assert summary.gmv == Decimal("0.00")
    assert summary.aov == Decimal("0.00")
    assert summary.status_breakdown == []
