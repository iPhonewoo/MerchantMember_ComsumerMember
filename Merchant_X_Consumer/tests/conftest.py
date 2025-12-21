import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from member.models import Member, Merchant
from store.models import Store

User = get_user_model()


@pytest.fixture
def api_client():
    """
    共用的 DRF APIClient。
    之後所有測試要打 /member/...、/store/... API，都用這個。
    """
    return APIClient()


@pytest.fixture
def create_member_user():
    """
    產生「一個 user + 一個 Member」的測試資料。

    用法：
        user, member = create_member_user()
    """
    def _create(username="member1"):
        user = User.objects.create_user(
            username=username,
            password="test1234",
            role="member",
        )
        member = Member.objects.create(
            user=user,
            name=f"{username}-name",
        )
        return user, member

    return _create


@pytest.fixture
def create_merchant_user():
    """
    產生「一個商家 user + 一個 Merchant + 一個 Store」。

    用法：
        user, merchant, store = create_merchant_user()
    """
    def _create(username="merchant1"):
        user = User.objects.create_user(
            username=username,
            password="test1234",
            role="merchant",
        )
        merchant = Merchant.objects.create(user=user)
        store = Store.objects.create(
            merchant=merchant,
            name=f"{username} 的商店",
            address="高雄市某處",
            description="測試商店",
        )
        return user, merchant, store

    return _create

