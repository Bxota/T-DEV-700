import pytest
from unittest.mock import patch
from db_manager.models import Teams
from db_manager.repositories.team_repository import TeamRepository

@pytest.mark.django_db
def test_get_teams_exception():
    with patch.object(Teams.objects, "order_by", side_effect=Exception("DB down")):
        res = TeamRepository.get_teams()
        assert res == {"error": "DB down"}

@pytest.mark.django_db
def test_create_team_exception_on_exists_check():
    # filter(...).exists() lève -> except
    mock_qs = patch.object(Teams.objects, "filter").start()
    mock_qs.return_value.exists.side_effect = Exception("exists failed")
    res = TeamRepository.create_team("A")
    assert res == {"error": "exists failed"}
    patch.stopall()

@pytest.mark.django_db
def test_create_team_exception_on_create():
    with patch.object(Teams.objects, "filter") as mock_filter:
        mock_filter.return_value.exists.return_value = False
        with patch.object(Teams.objects, "create", side_effect=Exception("create failed")):
            res = TeamRepository.create_team("A")
            assert res == {"error": "create failed"}

@pytest.mark.django_db
def test_get_team_by_id_generic_exception():
    # autre qu’un DoesNotExist -> except générique
    with patch.object(Teams.objects, "get", side_effect=RuntimeError("weird")):
        res = TeamRepository.get_team_by_id(123)
        assert res == {"error": "weird"}

@pytest.mark.django_db
def test_update_team_generic_exception_on_save():
    # get OK puis save lève -> except générique
    team = Teams(id=1, name="A")
    with patch.object(Teams.objects, "get", return_value=team):
        with patch.object(Teams, "save", side_effect=Exception("write error")):
            res = TeamRepository.update_team(1, "B")
            assert res == {"error": "write error"}
            
@pytest.mark.django_db
def test_update_team_doesnotexist_exception_on_save():
    # get OK puis save lève -> except générique
    team = Teams(id=1, name="A")
    with patch.object(Teams.objects, "get", return_value=team):
        with patch.object(Teams, "save", side_effect=Teams.DoesNotExist):
            res = TeamRepository.update_team(2, "B")
            assert res == {"error": "Team not found."}

@pytest.mark.django_db
def test_delete_team_generic_exception_on_delete():
    team = Teams(id=1, name="A")
    with patch.object(Teams.objects, "get", return_value=team):
        with patch.object(Teams, "delete", side_effect=Exception("cannot delete")):
            res = TeamRepository.delete_team(1)
            assert res == {"error": "cannot delete"}
            
@pytest.mark.django_db
def test_delete_team_doesnotexist_exception_on_save():
    # get OK puis save lève -> except générique
    team = Teams(id=1, name="A")
    with patch.object(Teams.objects, "get", return_value=team):
        with patch.object(Teams, "delete", side_effect=Teams.DoesNotExist):
            res = TeamRepository.delete_team(2)
            assert res == {"error": "Team not found."}