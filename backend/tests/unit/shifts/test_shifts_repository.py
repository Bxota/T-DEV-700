from datetime import datetime, timedelta, timezone

import pytest

from db_manager.models import Roles, Teams, Users, Shifts
from db_manager.repositories.shifts_repository import ShiftRepository, _ensure_datetime


@pytest.fixture
def user(db):
    team = Teams.objects.create(name="RepoShift")
    role, _ = Roles.objects.get_or_create(name="EmployeeShift")
    return Users.objects.create_user(
        email="shift@example.com",
        password="pwd",
        first_name="Shift",
        last_name="Worker",
        team=team,
        role=role,
    )


@pytest.mark.django_db
def test_create_update_check_in_out(user):
    start = datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)

    shift = ShiftRepository.create_shift(user=user, start_time=start.isoformat(), end_time=end.isoformat())
    assert isinstance(shift, Shifts)
    assert shift.start_time == start

    new_start = start + timedelta(hours=1)
    new_end = end + timedelta(hours=1)
    updated = ShiftRepository.update_shift(shift.id, new_start.isoformat(), new_end.isoformat())
    assert updated.start_time == new_start

    checked_in = ShiftRepository.check_in(shift.id, new_start.isoformat())
    assert checked_in.real_start_time == new_start

    checked_out = ShiftRepository.check_out(shift.id, new_end.isoformat())
    assert checked_out.real_end_time == new_end

    listed = ShiftRepository.get_shifts_by_user_id(user.id)
    assert listed.count() == 1

    deleted = ShiftRepository.delete_shift(shift.id)
    assert deleted is True


@pytest.mark.django_db
def test_get_shifts_returns_list(user):
    shift = ShiftRepository.create_shift(
        user=user,
        start_time=datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc),
        end_time=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    data = ShiftRepository.get_shifts()
    assert {"id": shift.id} in data


def test_get_shifts_returns_api_exception_on_error(monkeypatch):
    def raise_fail(*args, **kwargs):
        raise Exception("fail")

    monkeypatch.setattr("db_manager.repositories.shifts_repository.Shifts.objects.order_by", raise_fail)
    result = ShiftRepository.get_shifts()
    from rest_framework.exceptions import APIException
    assert isinstance(result, APIException)


def test_ensure_datetime_parses_iso_with_z():
    result = _ensure_datetime("2025-01-02T08:30:00Z")
    assert isinstance(result, datetime)
    assert result.tzinfo is not None


@pytest.mark.django_db
def test_check_in_shift_not_found_returns_error_dict():
    response = ShiftRepository.check_in(9999, datetime.now(timezone.utc).isoformat())
    assert response == {"error": "Shift not found."}


@pytest.mark.django_db
def test_check_out_returns_error_message_on_exception(monkeypatch):
    def raise_boom(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr("db_manager.repositories.shifts_repository.Shifts.objects.get", raise_boom)
    response = ShiftRepository.check_out(1, datetime.now(timezone.utc).isoformat())
    assert response == {"error": "boom"}


@pytest.mark.django_db
def test_list_shifts_by_user_id_and_date_filters(user):
    start = datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    shift = ShiftRepository.create_shift(user=user, start_time=start, end_time=end)

    qs = ShiftRepository.list_shifts_by_user_id_and_date(
        user_id=user.id,
        start=start - timedelta(minutes=30),
        end=end + timedelta(minutes=30),
    )
    assert list(qs.values_list("id", flat=True)) == [shift.id]
