import pytest
from db_manager.models import Teams
from db_manager.repositories.team_repository import TeamRepository

@pytest.mark.django_db
class TestTeamRepository:
    def test_create_team_success(self):
        team = TeamRepository.create_team("Equipe A")
        assert team.name == "Equipe A"

    def test_create_team_duplicate(self):
        Teams.objects.create(name="Equipe A")
        result = TeamRepository.create_team("Equipe A")
        assert result["error"] == "Team with this name already exists."

    def test_get_teams(self):
        Teams.objects.create(name="Equipe A")
        Teams.objects.create(name="Equipe B")
        teams = TeamRepository.get_teams()
        assert len(teams) == 2
        assert teams[0]["name"] == "Equipe A"

    def test_get_team_by_id_found(self):
        team = Teams.objects.create(name="Equipe A")
        result = TeamRepository.get_team_by_id(team.id)
        assert result.name == "Equipe A"

    def test_get_team_by_id_not_found(self):
        result = TeamRepository.get_team_by_id(999)
        assert result["error"] == "Team not found."

    def test_update_team_success(self):
        team = Teams.objects.create(name="Equipe A")
        updated = TeamRepository.update_team(team.id, "Equipe B")
        assert updated.name == "Equipe B"

    def test_delete_team_success(self):
        team = Teams.objects.create(name="Equipe A")
        result = TeamRepository.delete_team(team.id)
        assert result is True
        assert Teams.objects.count() == 0