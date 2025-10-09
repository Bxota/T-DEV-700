import pytest

COLLECTION = "/api/teams/"
DETAIL = "/api/teams/{id}/"
REPORTS = "/api/teams/{id}/reports/"


# -----------------------------
# TeamCollection (GET / POST)
# -----------------------------
@pytest.mark.django_db
def test_list_teams_ok(api_client, auth_headers, monkeypatch):
    # On mock le service pour contrôler la réponse
    from api.teams import service as team_service
    monkeypatch.setattr(team_service.TeamManager, "list_teams", lambda: [{"id": 1, "name": "Ops"}])

    r = api_client.get(COLLECTION, **auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "teams" in data and isinstance(data["teams"], list)
    assert data["teams"][0]["name"] == "Ops"
    
@pytest.mark.django_db
def test_list_teams_error_http(api_client, auth_headers, monkeypatch):
    # On mock le service pour contrôler la réponse
    from api.teams import service as team_service
    monkeypatch.setattr(team_service.TeamManager, "list_teams", lambda: [{"id": 1, "name": "Ops"}])

    r = api_client.put(COLLECTION, **auth_headers)
    print(r.json().get("error"))
    assert r.status_code == 405

@pytest.mark.django_db
def test_list_teams_error(api_client, auth_headers, monkeypatch):
    from api.teams import service as team_service
    monkeypatch.setattr(team_service.TeamManager, "list_teams", lambda: {"error": "boom"})

    r = api_client.get(COLLECTION, **auth_headers)
    assert r.status_code == 400
    assert r.json().get("error") == "boom"


@pytest.mark.django_db
def test_create_team_forbidden_without_permission(api_client, auth_headers, manager_role):
    payload = {"name": "Ops"}
    r = api_client.post(COLLECTION, payload, format="json", **auth_headers)
    assert r.status_code == 403


@pytest.mark.django_db
def test_create_team_ok_with_permission(api_client, auth_headers, monkeypatch):
    # Force la permission custom à True
    from api.permissions import HasTeamTagPermission
    monkeypatch.setattr(HasTeamTagPermission, "has_permission", lambda self, request, view: True)

    # Mock du service de création
    from api.teams import service as team_service

    class FakeTeam:
        def __init__(self, name):
            self.name = name

    monkeypatch.setattr(team_service.TeamManager, "create_team", lambda name: FakeTeam(name))

    payload = {"name": "Ops"}
    r = api_client.post(COLLECTION, payload, format="json", **auth_headers)
    assert r.status_code == 201
    assert r.json() == {"is_created": True, "name": "Ops"}


# -----------------------------
# TeamDetail (GET / PUT / DELETE)
# -----------------------------
@pytest.mark.django_db
def test_get_team_ok(api_client, auth_headers, monkeypatch):
    from api.teams import service as team_service

    class FakeTeam:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    monkeypatch.setattr(team_service.TeamManager, "get_team_by_id", lambda team_id: FakeTeam(1, "Ops"))

    r = api_client.get(DETAIL.format(id=1), **auth_headers)
    assert r.status_code == 200
    assert r.json() == {"id": 1, "name": "Ops"}


@pytest.mark.django_db
def test_get_team_not_found(api_client, auth_headers, monkeypatch):
    from api.teams import service as team_service
    monkeypatch.setattr(team_service.TeamManager, "get_team_by_id", lambda team_id: {"error": "not found"})

    r = api_client.get(DETAIL.format(id=999), **auth_headers)
    assert r.status_code == 404
    assert r.json().get("error")


@pytest.mark.django_db
def test_update_team_forbidden_without_permission(api_client, auth_headers, manager_role):
    payload = {"name": "NewName"}
    r = api_client.put(DETAIL.format(id=1), payload, format="json", **auth_headers)
    assert r.status_code == 403


@pytest.mark.django_db
def test_update_team_validation_error(api_client, auth_headers, monkeypatch):
    # Autorise la permission pour atteindre la validation de la vue
    from api.permissions import HasTeamTagPermission
    monkeypatch.setattr(HasTeamTagPermission, "has_permission", lambda self, request, view: True)

    r = api_client.put(DETAIL.format(id=1), {}, format="json", **auth_headers)
    assert r.status_code == 400
    assert r.json().get("error")


@pytest.mark.django_db
def test_update_team_ok_with_permission(api_client, auth_headers, monkeypatch):
    from api.permissions import HasTeamTagPermission
    monkeypatch.setattr(HasTeamTagPermission, "has_permission", lambda self, request, view: True)

    from api.teams import service as team_service

    class FakeTeam:
        def __init__(self, name):
            self.name = name

    monkeypatch.setattr(team_service.TeamManager, "update_team", lambda team_id, name: FakeTeam(name))

    payload = {"name": "NewName"}
    r = api_client.put(DETAIL.format(id=1), payload, format="json", **auth_headers)
    assert r.status_code == 200
    assert r.json() == {"is_updated": True, "new_name": "NewName"}


@pytest.mark.django_db
def test_delete_team_forbidden_without_permission(api_client, auth_headers, manager_role):
    r = api_client.delete(DETAIL.format(id=1), **auth_headers)
    assert r.status_code == 403


@pytest.mark.django_db
def test_delete_team_ok_with_permission(api_client, auth_headers, monkeypatch):
    from api.permissions import HasTeamTagPermission
    monkeypatch.setattr(HasTeamTagPermission, "has_permission", lambda self, request, view: True)

    from api.teams import service as team_service
    monkeypatch.setattr(team_service.TeamManager, "delete_team", lambda team_id: True)

    r = api_client.delete(DETAIL.format(id=1), **auth_headers)
    assert r.status_code == 200
    assert r.json() == {"is_deleted": True}


# -----------------------------
# GET /api/teams/reports/
# -----------------------------
@pytest.mark.django_db
def test_get_team_reports_requires_permission(api_client, auth_headers, manager_role):
    r = api_client.get(REPORTS.format(id=1), **auth_headers)
    assert r.status_code == 403


# @pytest.mark.django_db
# def test_get_team_reports_ok(api_client, auth_headers, monkeypatch, manager_role):
#     from api.permissions import HasTeamTagPermission
#     monkeypatch.setattr(HasTeamTagPermission, "has_permission", lambda self, request, view: True)

#     r = api_client.get(REPORTS.format(id=1), **auth_headers)
#     assert r.status_code == 200
#     # La vue retourne actuellement un objet vide
#     assert r.json() == {}
