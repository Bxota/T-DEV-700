import pytest

from test_CONSTANTS import *

@pytest.mark.django_db
def test_protected_route_requires_token(api_client):
    resp = api_client.get(WHOAMI)
    assert resp.status_code == 401
    
@pytest.mark.django_db
def test_protected_route_with_jwt(api_client, auth_headers):
    resp = api_client.get(WHOAMI, **auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user" in data and "email" in data["user"] and data["user"]["email"]

@pytest.mark.django_db
def test_expired_token_is_rejected(api_client, expired_headers):
    resp = api_client.get(WHOAMI, **expired_headers)
    print(resp.json())
    assert resp.status_code in (401, 403)