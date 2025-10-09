import pytest
from unittest.mock import patch
from api.teams.service import TeamManager
from db_manager.repositories.team_repository import TeamRepository

def test_list_teams_delegates_to_repo():
    with patch.object(TeamRepository, "get_teams", return_value=[{"id": 1, "name": "A"}]) as mock_get:
        res = TeamManager.list_teams()
        mock_get.assert_called_once_with()
        assert res == [{"id": 1, "name": "A"}]

def test_create_team_delegates_and_returns_value():
    with patch.object(TeamRepository, "create_team", return_value={"id": 2, "name": "B"}) as mock_create:
        res = TeamManager.create_team("B")
        mock_create.assert_called_once_with("B")
        assert res == {"id": 2, "name": "B"}

def test_create_team_propagates_error():
    with patch.object(TeamRepository, "create_team", return_value={"error": "Team exists"}) as mock_create:
        res = TeamManager.create_team("A")
        mock_create.assert_called_once_with("A")
        assert res == {"error": "Team exists"}
        
def test_get_team_by_id_delegates_correctly():
    fake_team = {"id": 1, "name": "Team A"}
    with patch.object(TeamRepository, "get_team_by_id", return_value=fake_team) as mock_get:
        res = TeamManager.get_team_by_id(1)

        mock_get.assert_called_once_with(1)
        assert res == fake_team
        
def test_get_team_by_id_returns_error():
    error = {"error": "Team not found"}
    with patch.object(TeamRepository, "get_team_by_id", return_value=error) as mock_get:
        res = TeamManager.get_team_by_id(42)

        mock_get.assert_called_once_with(42)
        assert res == error
        
def test_update_team():
    with patch.object(TeamRepository, "update_team", return_value={"id": 1, "name": "C"}) as mock_update:
        res = TeamManager.update_team(1, "C")
        mock_update.assert_called_once_with(1, "C")
        assert res == {"id": 1, "name": "C"}

def test_delete_team_delegates_correctly():
    with patch.object(TeamRepository, "delete_team", return_value=True) as mock_delete:
        res = TeamManager.delete_team(1)

        mock_delete.assert_called_once_with(1)
        assert res is True
        
def test_delete_team_returns_error():
    with patch.object(TeamRepository, "delete_team", return_value={"error": "Team not found"}) as mock_delete:
        res = TeamManager.delete_team(99)

        mock_delete.assert_called_once_with(99)
        assert res == {"error": "Team not found"}