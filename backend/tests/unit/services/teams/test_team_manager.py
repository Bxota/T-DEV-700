import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call

from django.db.models import F

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


def test_compute_lateness_stats_returns_rate_and_count():
    shifts = MagicMock()
    exclude_qs = MagicMock()
    filter_qs = MagicMock()
    exclude_qs.count.return_value = 4
    filter_qs.count.return_value = 1
    shifts.exclude.return_value = exclude_qs
    shifts.filter.return_value = filter_qs

    lateness_rate, late_count = TeamManager.compute_lateness_stats(shifts)

    shifts.exclude.assert_called_once_with(real_start_time__isnull=True)
    shifts.filter.assert_called_once_with(real_start_time__gt=F("start_time"))
    assert lateness_rate == 25.0
    assert late_count == 1


def test_compute_lateness_stats_returns_none_when_no_checkins():
    shifts = MagicMock()
    exclude_qs = MagicMock()
    filter_qs = MagicMock()
    exclude_qs.count.return_value = 0
    filter_qs.count.return_value = 0
    shifts.exclude.return_value = exclude_qs
    shifts.filter.return_value = filter_qs

    lateness_rate, late_count = TeamManager.compute_lateness_stats(shifts)

    assert lateness_rate is None
    assert late_count is None


@patch("api.teams.service.now")
def test_compute_absences_stats_returns_rate_and_count(mock_now):
    mock_now.return_value = datetime(2024, 1, 1, 12, 0, 0)
    shifts = MagicMock()
    shifts.count.return_value = 5
    absence_qs = MagicMock()
    absence_qs.count.return_value = 2
    shifts.filter.return_value = absence_qs

    absences_rate, absences_count = TeamManager.compute_absences_stats(shifts)

    shifts.count.assert_called_once_with()
    shifts.filter.assert_called_once_with(
        real_start_time__isnull=True,
        real_end_time__isnull=True,
        end_time__lt=mock_now.return_value,
    )
    assert absences_rate == 40.0
    assert absences_count == 2


@patch("api.teams.service.now")
def test_compute_absences_stats_returns_none_when_no_shifts(mock_now):
    mock_now.return_value = datetime(2024, 1, 1, 12, 0, 0)
    shifts = MagicMock()
    shifts.count.return_value = 0
    shifts.filter.return_value.count.return_value = 0

    absences_rate, absences_count = TeamManager.compute_absences_stats(shifts)

    assert absences_rate is None
    assert absences_count is None


def test_compute_total_worked_minutes_accumulates_duration():
    shift_a = SimpleNamespace(
        real_start_time=datetime(2024, 1, 1, 8, 0, 0),
        real_end_time=datetime(2024, 1, 1, 9, 30, 30),
    )
    shift_b = SimpleNamespace(
        real_start_time=datetime(2024, 1, 2, 13, 0, 0),
        real_end_time=datetime(2024, 1, 2, 14, 0, 0),
    )
    shifts = MagicMock()
    shifts.filter.return_value = [shift_a, shift_b]

    total_minutes = TeamManager.compute_total_worked_minutes(shifts)

    shifts.filter.assert_called_once_with(
        real_start_time__isnull=False,
        real_end_time__isnull=False,
    )
    assert total_minutes == pytest.approx(150.5)


@patch.object(TeamManager, "compute_total_worked_minutes", return_value=180.0)
@patch.object(TeamManager, "compute_absences_stats", return_value=(10.0, 1))
@patch.object(TeamManager, "compute_lateness_stats", return_value=(20.0, 2))
def test_generate_user_kpi_report_aggregates_metrics(mock_late, mock_absence, mock_minutes):
    user = SimpleNamespace(id=7)
    shifts = MagicMock()
    shifts.count.return_value = 6

    report = TeamManager.generate_user_kpi_report(user, shifts)

    mock_late.assert_called_once_with(shifts)
    mock_absence.assert_called_once_with(shifts)
    mock_minutes.assert_called_once_with(shifts)
    assert report == {
        "user_id": 7,
        "lateness_rate": 20.0,
        "lateness_count": 2,
        "absences_rate": 10.0,
        "absences_count": 1,
        "total_shifts": 6,
        "total_worked_minutes": 180.0,
    }


@patch("api.teams.service.Shifts")
def test_generate_team_kpi_report_without_filters(mock_shifts):
    members_qs = MagicMock()
    members_qs.count.return_value = 3

    shifts_qs = MagicMock()
    shifts_qs.aggregate.return_value = {
        "total_shifts": 5,
        "total_with_checkin": 4,
        "late_shifts": 1,
        "absence_shifts": 2,
        "worked_duration": timedelta(minutes=150),
    }
    mock_shifts.objects.filter.return_value = shifts_qs

    report = TeamManager.generate_team_kpi_report(members_qs)

    mock_shifts.objects.filter.assert_called_once_with(user__in=members_qs)
    assert report == {
        "members": 3,
        "total_shifts": 5,
        "total_with_checkin": 4,
        "lateness_count": 1,
        "lateness_rate": 25.0,
        "absences_count": 2,
        "absences_rate": 40.0,
        "total_worked_minutes": 150,
    }


@patch("api.teams.service.Shifts")
def test_generate_team_kpi_report_applies_date_filters(mock_shifts):
    members_qs = MagicMock()
    members_qs.count.return_value = 2
    shifts_qs = MagicMock()
    shifts_qs.filter.side_effect = [shifts_qs, shifts_qs]
    shifts_qs.aggregate.return_value = {
        "total_shifts": 0,
        "total_with_checkin": 0,
        "late_shifts": 0,
        "absence_shifts": 0,
        "worked_duration": None,
    }
    mock_shifts.objects.filter.return_value = shifts_qs

    start = datetime(2024, 1, 1)
    end = datetime(2024, 2, 1)

    report = TeamManager.generate_team_kpi_report(members_qs, start=start, end=end)

    shifts_qs.filter.assert_has_calls(
        [
            call(start_time__gte=start),
            call(start_time__lt=end),
        ]
    )
    assert report["lateness_rate"] is None
    assert report["absences_rate"] is None
    assert report["total_worked_minutes"] == 0
