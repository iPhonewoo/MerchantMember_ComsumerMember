import factory
from store.models import Store
from .user_factory import MerchantFactory


class StoreFactory(factory.django.DjangoModelFactory):
    """
    Store 工廠，用來建立商店。

    重點：
    - merchant 欄位使用 MerchantFactory，自動建立「商家 + user」
    - name / address / description 都給合理的預設值
    """

    class Meta:
        model = Store

    merchant = factory.SubFactory(MerchantFactory)
    name = factory.Sequence(lambda n: f"測試商店{n}")
    address = "高雄市高雄區高雄街 1 號"
    description = "這是一家測試用的商店"
