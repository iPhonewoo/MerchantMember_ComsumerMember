import pytest
from decimal import Decimal
from tests.factories.order_factory import OrderFactory, OrderItemFactory
from tests.factories.user_factory import MemberFactory
from store.models import Order


@pytest.mark.django_db
def test_member_can_update_own_order_address(api_client):
    member = MemberFactory()
    user = member.user
    order = OrderFactory(member=member)

    api_client.force_authenticate(user=user)

    res = api_client.patch(f"/store/orders/{order.id}/", {
        "address": "新地址 123 號"
    }, format="json")

    assert res.status_code == 200
    order.refresh_from_db()
    assert order.address == "新地址 123 號"


@pytest.mark.django_db
def test_order_status_transition_valid(api_client):
    """
    測試 can_transition 規則：
    pending -> paid 可以
    """
    member = MemberFactory()
    user = member.user
    order = OrderFactory(member=member, status=Order.StatusChoices.PENDING)

    api_client.force_authenticate(user=user)

    res = api_client.patch(f"/store/orders/{order.id}/", {
        "status": Order.StatusChoices.PAID
    }, format="json")

    assert res.status_code == 200
    order.refresh_from_db()
    assert order.status == Order.StatusChoices.PAID


@pytest.mark.django_db
def test_order_status_transition_invalid(api_client):
    """
    測試不合法轉換（例如：completed -> paid）會被擋
    """
    member = MemberFactory()
    user = member.user
    order = OrderFactory(member=member, status=Order.StatusChoices.COMPLETED)

    api_client.force_authenticate(user=user)

    res = api_client.patch(f"/store/orders/{order.id}/", {
        "status": Order.StatusChoices.PAID
    }, format="json")

    assert res.status_code == 400
    assert "訂單無法從" in str(res.data)
