import pytest

@pytest.mark.django_db
def test_delete_team_forbidden_without_permission(api_client, auth_headers):
    from db_manager.models import Teams
    team = Teams.objects.create(name="team1")
    r = api_client.delete(f"/api/teams/{team.id}/", **auth_headers)
    assert r.status_code == 403