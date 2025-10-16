from datetime import date, time

import pytest

from db_manager.models import (
    Roles,
    Teams,
    Users,
    ShiftTemplate,
    ShiftRule,
)
from db_manager.repositories.shift_template_repository import ShiftTemplateRepository
from db_manager.repositories.shift_rule_repository import ShiftRuleRepository
from db_manager.repositories.shift_exception_repository import ShiftExceptionRepository


@pytest.fixture
def base_data(db):
    team = Teams.objects.create(name="Repo Team")
    role = Roles.objects.create(name="EmployeeRepo")
    manager_role = Roles.objects.create(name="ManagerRepo")
    creator = Users.objects.create_user(
        email="creator@example.com",
        password="pwd",
        first_name="Cre",
        last_name="Ator",
        team=team,
        role=manager_role,
    )
    return team, role, creator


@pytest.mark.django_db
def test_shift_template_repository_create_and_update(base_data):
    team, role, creator = base_data
    tpl = ShiftTemplateRepository.create_template(
        name="Tpl",
        team_id=team.id,
        created_by_id=creator.id,
        default_duration_minutes=300,
        role_id=None,
    )
    assert isinstance(tpl, ShiftTemplate)

    updated = ShiftTemplateRepository.update_template(tpl.id, name="Updated", role_id=role.id)
    assert updated.name == "Updated"
    assert updated.role_id == role.id

    active_list = ShiftTemplateRepository.list_by_team(team.id, active_only=True)
    assert active_list.count() == 1

    ShiftTemplateRepository.set_active(tpl.id, False)
    assert ShiftTemplate.objects.get(id=tpl.id).is_active is False


@pytest.mark.django_db
def test_shift_rule_repository_assign_and_clear(base_data):
    team, role, creator = base_data
    tpl = ShiftTemplateRepository.create_template(
        name="Morning",
        team_id=team.id,
        created_by_id=creator.id,
        default_duration_minutes=480,
    )

    rule = ShiftRuleRepository.create_rule(
        template_id=tpl.id,
        weekday=date.today().weekday(),
        start_local_time=time(8, 0),
        duration_minutes=480,
        effective_from=date.today(),
        effective_to=None,
        apply_to_whole_team=False,
        assigned_user_ids=None,
    )
    assert isinstance(rule, ShiftRule)

    ShiftRuleRepository.update_rule(rule.id, apply_to_whole_team=True)
    rule.refresh_from_db()
    assert rule.apply_to_whole_team is True

    ShiftRuleRepository.assign_users(rule.id, [creator.id])
    assert rule.assigned_users.count() == 1

    ShiftRuleRepository.clear_assigned_users(rule.id)
    assert rule.assigned_users.count() == 0

    fetched = ShiftRuleRepository.get_by_id(rule.id)
    assert fetched.id == rule.id


@pytest.mark.django_db
def test_shift_exception_repository_create_update_delete(base_data):
    team, role, creator = base_data
    tpl = ShiftTemplateRepository.create_template(
        name="Night",
        team_id=team.id,
        created_by_id=creator.id,
        default_duration_minutes=480,
    )
    rule = ShiftRuleRepository.create_rule(
        template_id=tpl.id,
        weekday=date.today().weekday(),
        start_local_time=time(10, 0),
        duration_minutes=240,
        effective_from=date.today(),
        effective_to=None,
        apply_to_whole_team=True,
        assigned_user_ids=None,
    )

    exc = ShiftExceptionRepository.create_exception(
        rule_id=rule.id,
        date_value=date.today(),
        is_skipped=False,
    )
    assert exc.rule_id == rule.id

    updated = ShiftExceptionRepository.update_exception(exc.id, note="Updated note")
    assert updated.note == "Updated note"

    listed = ShiftExceptionRepository.list_by_rule(rule.id)
    assert listed.count() == 1

    ShiftExceptionRepository.delete_exception(exc.id)
    assert ShiftExceptionRepository.get_by_id(exc.id) == {"error": "ShiftException not found"}
