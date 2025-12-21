import factory
from django.contrib.auth import get_user_model
from member.models import Member, Merchant
from store.models import Store

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """
    基本 User 工廠，可以指定 role=member / merchant / admin
    """
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "test1234")
    email = factory.LazyAttribute(lambda o: f"{o.username}@test.com")
    role = "member"  # 預設是 member


class MemberFactory(factory.django.DjangoModelFactory):
    """
    Member Profile。若沒給 user，會自動幫你建一個 role=member 的 user。
    """
    class Meta:
        model = Member

    user = factory.SubFactory(UserFactory, role="member")
    name = factory.Sequence(lambda n: f"會員{n}")


class MerchantFactory(factory.django.DjangoModelFactory):
    """
    Merchant Profile。同樣自動建立對應 user。
    """
    class Meta:
        model = Merchant

    user = factory.SubFactory(UserFactory, role="merchant")

    @factory.post_generation
    def create_store(self, create, extracted, **kwargs):
        """
        測試環境中，每生成一個 Merchant，就自動產生對應的 Store。
        就像 RegisterSerializer 的邏輯一樣。
        """
        if not create:
            return
        Store.objects.create(
            merchant=self,
            name=f"{self.user.username} 的商店",
            address="測試地址",
            description="測試商店描述",
        )
