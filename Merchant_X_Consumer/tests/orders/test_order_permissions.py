import pytest
from tests.factories.order_factory import OrderFactory
from tests.factories.user_factory import MemberFactory, MerchantFactory
from tests.factories.store_factory import StoreFactory
from tests.factories.product_factory import ProductFactory
from store.models import Order, Store


@pytest.mark.django_db
def test_member_cannot_view_other_member_order(api_client):
    memberA = MemberFactory()
    memberB = MemberFactory()
    order = OrderFactory(member=memberA)

    api_client.force_authenticate(user=memberB.user)

    res = api_client.get(f"/store/orders/{order.id}/")

    assert res.status_code in (403, 404)


@pytest.mark.django_db
def test_merchant_can_view_order_with_own_product(api_client):
    merchant = MerchantFactory()
    store = Store.objects.get(merchant=merchant)
    product = ProductFactory(store=store)

    member = MemberFactory()
    order = OrderFactory(member=member)
    order.items.create(
        product=product,
        quantity=1,
        price_at_purchase=product.price,
    )

    api_client.force_authenticate(user=merchant.user)

    res = api_client.get(f"/store/orders/{order.id}/")

    assert res.status_code == 200
    assert res.data["order_number"] == order.order_number
