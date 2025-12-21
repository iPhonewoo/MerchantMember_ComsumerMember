import pytest
from decimal import Decimal
from tests.factories.user_factory import MemberFactory, MerchantFactory
from tests.factories.store_factory import StoreFactory
from tests.factories.product_factory import ProductFactory
from store.models import Order, Store


@pytest.mark.django_db
def test_member_can_create_order(api_client):
    """
    測試建立訂單流程：
    - 建立一個商家 + 商店 + 兩個商品
    - 建立一個會員
    - 會員登入後呼叫 POST /store/orders/
    - 檢查：
        * 回傳 201
        * total_amount 正確
        * 商品庫存有被扣除
        * Order 的 member 是這個會員
    """

    # 商家 + 商店 + 商品
    merchant = MerchantFactory()
    store = Store.objects.get(merchant=merchant)

    product1 = ProductFactory(store=store, price=Decimal("5.00"), stock=10)
    product2 = ProductFactory(store=store, price=Decimal("10.00"), stock=5)

    # 會員 + 登入
    member = MemberFactory()
    user = member.user
    api_client.force_authenticate(user=user)

    payload = {
        "receiver_name": "王小明",
        "receiver_phone": "0912345678",
        "address": "高雄市哪裡哪裡",
        "note": "請小心包裝",
        "items": [
            {"product": product1.id, "quantity": 2},  # 2 * 5 = 10
            {"product": product2.id, "quantity": 1},  # 1 * 10 = 10
        ]
    }

    res = api_client.post("/store/orders/", payload, format="json")

    assert res.status_code == 201

    order = Order.objects.get(order_number=res.data["order_number"])
    assert order.member == member
    assert order.total_amount == Decimal("20.00")

    # 檢查庫存有被扣除
    product1.refresh_from_db()
    product2.refresh_from_db()
    assert product1.stock == 8
    assert product2.stock == 4
