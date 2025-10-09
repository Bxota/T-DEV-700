import pytest
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_token_obtain_pair(api_client):
    User = get_user_model()
    User.objects.create_user(email="t@example.com", password="pw1234")
    r = api_client.post("/api/token/", {"email": "t@example.com", "password": "pw1234"}, format="json")
    assert r.status_code == 200
    body = r.json()
    assert "access" in body and "refresh" in body
    
@pytest.mark.django_db
def test_token_refresh_invalid(api_client):
    r = api_client.post("/api/token/refresh/", {"refresh": "bogus"}, format="json")
    assert r.status_code in (401, 400)