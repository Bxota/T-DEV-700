import pytest

PUBLIC = "/api/health/"
AUTH = "/api/health/auth/"
MANAGER = "/api/health/auth-manager/"


def test_health_ok(api_client):
    r = api_client.get(PUBLIC)
    assert r.status_code == 200


@pytest.mark.django_db
def test_health_authenticated_requires_token(api_client):
    r = api_client.get(AUTH)
    assert r.status_code == 401


@pytest.mark.django_db
def test_health_authenticated_ok(api_client, auth_headers):
    r = api_client.get(AUTH, **auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "message" in data


@pytest.mark.django_db
def test_health_manager_requires_permission(api_client, auth_headers):
    # Authentifié mais sans la permission custom -> 403
    r = api_client.get(MANAGER, **auth_headers)
    assert r.status_code == 403


@pytest.mark.django_db
def test_health_manager_with_permission(api_client, auth_headers, monkeypatch):
    # On ne teste pas la permission ici, seulement le contrôleur :
    # on force la permission à True pour vérifier le 200.
    from api.permissions import HasTeamTagPermission

    monkeypatch.setattr(
        HasTeamTagPermission,
        "has_permission",
        lambda self, request, view: True,
    )

    r = api_client.get(MANAGER, **auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "message" in data