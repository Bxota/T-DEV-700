from datetime import datetime, timedelta, timezone

import pytest

from db_manager.models import Roles, Teams, Users, Shifts
from db_manager.repositories.shifts_repository import ShiftRepository


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
