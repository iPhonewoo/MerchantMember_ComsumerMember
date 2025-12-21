import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from member.models import Member, Merchant
from store.models import Store

User = get_user_model()

@pytest.fixture
def api_client():
    """
    建立 DRF 專用的 API 測試 client。
    之後測試 POST/GET API 都用它發送。
    """
    return APIClient()


@pytest.fixture
def create_member_user():
    """
    建立一組「會員帳號 + Member Profile」的測試資料。
    為什麼用函式再回傳？因為 fixture 可以重複產生多組不互相干擾的資料。
    """
    def _create():
        # 建 user
        user = User.objects.create_user(
            username="member1",
            password="test1234",
            role="member"
        )
        # 一對一 Member profile
        member = Member.objects.create(
            user=user,
            name="測試會員",
        )
        return user, member

    return _create


@pytest.fixture
def create_merchant_user():
    """
    建立一組「商家 user + merchant profile + 商店」。
    讓測試建立產品 / 查看訂單時不必每次都手動建資料。
    """
    def _create():
        user = User.objects.create_user(
            username="merchant1",
            password="test1234",
            role="merchant"
        )
        merchant = Merchant.objects.create(user=user)
        store = Store.objects.create(
            merchant=merchant,
            name="測試商店",
            address="地址",
            description="描述"
        )
        return user, merchant, store

    return _create
