import pytest
from tests.factories.user_factory import MerchantFactory
from store.models import Store


@pytest.mark.django_db
def test_merchant_can_update_own_store(api_client):
    merchant = MerchantFactory()
    user = merchant.user
    store = Store.objects.get(merchant=merchant)

    api_client.force_authenticate(user=user)

    res = api_client.patch(f"/store/stores/{store.id}/", {
        "address": "高雄市新地址 123 號"
    }, format="json")

    assert res.status_code == 200
    assert res.data["address"] == "高雄市新地址 123 號"


@pytest.mark.django_db
def test_other_merchant_cannot_update_store(api_client):
    # 商家 A + 商店 A
    merchantA = MerchantFactory()
    storeA = Store.objects.get(merchant=merchantA)

    # 商家 B
    merchantB = MerchantFactory()
    userB = merchantB.user

    api_client.force_authenticate(user=userB)

    res = api_client.patch(f"/store/stores/{storeA.id}/", {
        "address": "我亂改的地址"
    }, format="json")

    # 會被 IsOwnerOfStore 擋
    assert res.status_code in (403, 404)
