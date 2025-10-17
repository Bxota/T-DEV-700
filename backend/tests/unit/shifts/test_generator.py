from datetime import date, time, timedelta

import pytest
from django.utils import timezone

from api.shifts.generator import generate_occurrences_for_window
from db_manager.models import (
    Roles,
    Teams,
    Users,
    ShiftTemplate,
    ShiftRule,
    ShiftException,
    Shifts,
)


@pytest.mark.django_db
def test_generate_occurrences_whole_team_creates_shifts():
    team = Teams.objects.create(name="Team")
    role, _ = Roles.objects.get_or_create(name="Employee")
    manager_role, _ = Roles.objects.get_or_create(name="Manager")

    manager = Users.objects.create_user(
        email="manager@example.com",
        password="pwd",
        first_name="Mana",
        last_name="Ger",
        team=team,
        role=manager_role,
    )
    staff = Users.objects.create_user(
        email="staff@example.com",
        password="pwd",
        first_name="Emp",
        last_name="Loyee",
        team=team,
        role=role,
    )

    tpl = ShiftTemplate.objects.create(
        name="Morning",
        team=team,
        created_by=manager,
        role=None,
        default_duration_minutes=480,
        timezone="UTC",
    )

    rule = ShiftRule.objects.create(
        template=tpl,
        weekday=date.today().weekday(),
        start_local_time=time(8, 0),
        duration_minutes=480,
        effective_from=date.today(),
        effective_to=None,
        apply_to_whole_team=True,
    )

    result = generate_occurrences_for_window(date.today(), date.today(), team_id=team.id)
    assert result["created"] >= 1
    assert Shifts.objects.filter(user=staff).count() == 1


@pytest.mark.django_db
def test_generate_occurrences_handles_exceptions_and_assignments():
    team = Teams.objects.create(name="TeamB")
    role, _ = Roles.objects.get_or_create(name="Employee")
    manager_role, _ = Roles.objects.get_or_create(name="Manager")

    manager = Users.objects.create_user(
        email="managerb@example.com",
        password="pwd",
        first_name="Mana",
        last_name="GerB",
        team=team,
        role=manager_role,
    )
    assignee = Users.objects.create_user(
        email="assignee@example.com",
        password="pwd",
        first_name="As",
        last_name="Signee",
        team=team,
        role=role,
    )

    tpl = ShiftTemplate.objects.create(
        name="Evening",
        team=team,
        created_by=manager,
        role=None,
        default_duration_minutes=240,
        timezone="UTC",
    )

    weekday = (date.today() + timedelta(days=1)).weekday()
    rule = ShiftRule.objects.create(
        template=tpl,
        weekday=weekday,
        start_local_time=time(15, 0),
        duration_minutes=240,
        effective_from=date.today(),
        effective_to=None,
        apply_to_whole_team=False,
    )
    rule.assigned_users.add(assignee)

    ShiftException.objects.create(
        rule=rule,
        date=date.today() + timedelta(days=1),
        is_skipped=True,
    )

    start = date.today()
    end = start + timedelta(days=3)
    result = generate_occurrences_for_window(start, end, team_id=team.id)
    assert result["created"] == 0

    # remove skip and override to test overrides
    ShiftException.objects.filter(rule=rule).delete()
    override_date = date.today() + timedelta(days=1)
    ShiftException.objects.create(
        rule=rule,
        date=override_date,
        is_skipped=False,
        override_start_local_time=time(17, 0),
        override_duration_minutes=120,
    )

    result = generate_occurrences_for_window(start, end, team_id=team.id)
    assert result["created"] == 1
    shift = Shifts.objects.get(user=assignee)
    assert shift.start_time.hour == 17
    assert shift.end_time - shift.start_time == timedelta(minutes=120)
