import pytest
from tests.factories.user_factory import MerchantFactory
from tests.factories.store_factory import StoreFactory
from store.models import Product, Store


@pytest.mark.django_db
def test_merchant_can_create_product_in_own_store(api_client):
    """
    測試商家可以新增商品：
    - 先建立商家 + 商店
    - 登入商家
    - 呼叫 POST /store/products/
    - 應該 201，且 product.store 是該商家的 store
    """

    merchant = MerchantFactory()
    user = merchant.user
    store = Store.objects.get(merchant=merchant)

    api_client.force_authenticate(user=user)

    res = api_client.post("/store/products/", {
        "name": "Q彈潔牙骨",
        "description": "狗狗愛吃",
        "price": "5.99",
        "stock": 20
    }, format="json")

    assert res.status_code == 201
    assert res.data["name"] == "Q彈潔牙骨"

    product = Product.objects.get(name="Q彈潔牙骨")
    assert product.store == store
