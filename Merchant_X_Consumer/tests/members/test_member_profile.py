import pytest
from tests.factories.user_factory import MemberFactory


@pytest.mark.django_db
def test_member_can_view_own_profile(api_client):
    """
    測試：
    - 會員登入後
    - 可以 GET /member/members/{id}/ 拿到自己的資料
    """

    member = MemberFactory()
    user = member.user

    # 模擬登入
    api_client.force_authenticate(user=user)

    url = f"/member/members/{member.id}/"
    res = api_client.get(url)

    assert res.status_code == 200
    assert res.data["name"] == member.name
    assert "orders" in res.data  # MemberSerializer 有帶 orders


@pytest.mark.django_db
def test_member_cannot_view_other_profile(api_client):
    """
    測試：
    - A 會員登入
    - 嘗試查看 B 會員資料
    - 會被擋（你的 IsOwnerOfMemberProfile 應該會讓 queryset or permission 回傳 403 / 404）
    """

    memberA = MemberFactory()
    memberB = MemberFactory()
    userA = memberA.user

    api_client.force_authenticate(user=userA)

    url = f"/member/members/{memberB.id}/"
    res = api_client.get(url)

    # 依你 ViewSet + permission 實作，可能是 403 或 404
    assert res.status_code in (403, 404)
