import pytest
from tests.factories.user_factory import MemberFactory


@pytest.mark.django_db
def test_member_can_login_and_get_token(api_client):
    # 建立會員 user + member profile
    member = MemberFactory()
    user = member.user

    response = api_client.post("/member/login/", {
        "username": user.username,
        "password": "test1234"
    })

    assert response.status_code == 200
    assert "access" in response.data
    assert response.data["username"] == user.username
    assert response.data["role"] == "member"
