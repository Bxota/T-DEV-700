from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.shifts.shift_gestion import views as shift_views
from db_manager.models import Roles, Teams, Users


@pytest.fixture
def manager_user(db):
    team = Teams.objects.create(name="Team API")
    manager_role = Roles.objects.create(name="manager")
    user = Users.objects.create_user(
        email="manager@example.com",
        password="pass",
        first_name="Mana",
        last_name="Ger",
        team=team,
        role=manager_role,
    )
    return user


@pytest.fixture
def api_client(manager_user):
    client = APIClient()
    client.force_authenticate(user=manager_user)
    return client


@pytest.fixture
def manager_team(manager_user):
    return manager_user.team


def patch_manager_attr(target, attribute, value):
    return patch.object(target, attribute, value)


def make_dummy_qs(items):
    class DummyQS(list):
        def order_by(self, *args, **kwargs):
            return self

    qs = DummyQS(items)
    return qs


@pytest.mark.django_db
def test_create_shift_template_success(api_client, manager_team, manager_user):
    url = f"/api/teams/{manager_team.id}/shift-templates"
    payload = {"name": "Morning", "default_duration_minutes": 480, "timezone": "UTC"}

    with patch_manager_attr(shift_views.ShiftTemplateManager, "create_template", MagicMock(return_value=MagicMock())), \
         patch_manager_attr(shift_views.ShiftTemplateManager, "check_db_return", MagicMock(return_value={"id": 1})):
        response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"id": 1}


@pytest.mark.django_db
def test_list_shift_templates_by_team(api_client, manager_team):
    url = f"/api/teams/{manager_team.id}/shift-templates/list"
    dummy_rule = MagicMock()

    with patch_manager_attr(shift_views.ShiftTemplateManager, "get_shift_template_by_team_id", MagicMock(return_value=make_dummy_qs([dummy_rule]))), \
         patch_manager_attr(shift_views.ShiftTemplateManager, "check_db_return", MagicMock(return_value=[{"id": 1}])):
        response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == [{"id": 1}]


@pytest.mark.django_db
def test_retrieve_shift_template(api_client, manager_team):
    url = f"/api/shift-templates/10"
    template = MagicMock(id=10)
    rule_instance = MagicMock(id=5)

    with patch_manager_attr(shift_views.ShiftTemplateManager, "get_shift_template_by_id", MagicMock(return_value=template)), \
         patch_manager_attr(shift_views.ShiftTemplateManager, "check_db_return", MagicMock(return_value={"id": 10})), \
         patch_manager_attr(shift_views.ShiftRuleManager, "get_shift_rule_by_template_id", MagicMock(return_value=make_dummy_qs([rule_instance]))), \
         patch_manager_attr(shift_views.ShiftRuleManager, "check_db_return", MagicMock(return_value={"id": 5})), \
         patch_manager_attr(shift_views.ShiftExceptionManager, "get_shift_exception_by_rule_id", MagicMock(return_value=make_dummy_qs([]))), \
         patch_manager_attr(shift_views.ShiftExceptionManager, "check_db_return", MagicMock(return_value=[])):
        response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["rules"] == [{"id": 5, "exceptions": []}]


@pytest.mark.django_db
def test_list_shift_rules_by_template(api_client):
    url = "/api/shift-templates/4/rules/list"

    with patch_manager_attr(shift_views.ShiftRuleManager, "get_shift_rule_by_template_id", MagicMock(return_value=make_dummy_qs([MagicMock()]))), \
         patch_manager_attr(shift_views.ShiftRuleManager, "check_db_return", MagicMock(return_value=[{"id": 4}])):
        response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == [{"id": 4}]


@pytest.mark.django_db
def test_retrieve_shift_rule(api_client):
    url = "/api/shift-rules/7"

    with patch_manager_attr(shift_views.ShiftRuleManager, "get_shift_rule_by_id", MagicMock(return_value=MagicMock(id=7))), \
         patch_manager_attr(shift_views.ShiftRuleManager, "check_db_return", MagicMock(return_value={"id": 7})), \
         patch_manager_attr(shift_views.ShiftExceptionManager, "get_shift_exception_by_rule_id", MagicMock(return_value=make_dummy_qs([]))), \
         patch_manager_attr(shift_views.ShiftExceptionManager, "check_db_return", MagicMock(return_value=[])):
        response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["exceptions"] == []


@pytest.mark.django_db
def test_add_shift_rule(api_client):
    url = "/api/shift-templates/9/rules"
    payload = {
        "weekday": 1,
        "start_local_time": "08:00:00",
        "duration_minutes": 60,
        "effective_from": "2025-01-01",
        "apply_to_whole_team": True,
    }

    with patch_manager_attr(shift_views.ShiftTemplateManager, "get_shift_template_by_id", MagicMock(return_value=MagicMock(id=9))), \
         patch("api.shifts.shift_gestion.views.ShiftRuleRepository.create_rule", return_value=MagicMock()), \
         patch_manager_attr(shift_views.ShiftRuleManager, "check_db_return", MagicMock(return_value={"id": 99})):
        response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"id": 99}


@pytest.mark.django_db
def test_assign_rule_users_whole_team(api_client, manager_user):
    url = "/api/shift-rules/11/assign-users"
    rule = MagicMock(id=11)
    rule.template.team_id = manager_user.team_id
    rule.template_id = 11
    rule.apply_to_whole_team = True
    rule.assigned_users.values_list.return_value = []
    rule.refresh_from_db = MagicMock()

    with patch_manager_attr(shift_views.ShiftRuleManager, "get_shift_rule_by_id", MagicMock(return_value=rule)), \
         patch_manager_attr(shift_views.ShiftRuleManager, "update_rule", MagicMock(return_value=rule)), \
         patch_manager_attr(shift_views.ShiftRuleManager, "check_db_return", MagicMock(return_value={"id": 11})), \
         patch_manager_attr(shift_views.ShiftRuleManager, "clear_assigned_users", MagicMock(return_value=True)):
        response = api_client.post(url, {"apply_to_whole_team": True}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["apply_to_whole_team"] is True


@pytest.mark.django_db
def test_assign_rule_users_subset(api_client, manager_user):
    url = "/api/shift-rules/12/assign-users"
    rule = MagicMock(id=12)
    rule.template.team_id = manager_user.team_id
    rule.template_id = 12
    rule.apply_to_whole_team = False
    rule.assigned_users.values_list.return_value = [1]

    with patch_manager_attr(shift_views.ShiftRuleManager, "get_shift_rule_by_id", MagicMock(return_value=rule)), \
         patch_manager_attr(shift_views.ShiftRuleManager, "assign_users", MagicMock(return_value=rule)):
        response = api_client.post(url, {"user_ids": [1]}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["assigned_user_ids"] == [1]


@pytest.mark.django_db
def test_add_shift_exception(api_client):
    url = "/api/shift-rules/15/exceptions"
    payload = {"date": "2025-01-01", "is_skipped": True}

    with patch_manager_attr(shift_views.ShiftRuleManager, "get_shift_rule_by_id", MagicMock(return_value=MagicMock(id=15))), \
         patch_manager_attr(shift_views.ShiftExceptionManager, "create_exception", MagicMock(return_value=MagicMock())), \
         patch_manager_attr(shift_views.ShiftExceptionManager, "check_db_return", MagicMock(return_value={"id": 51})):
        response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"id": 51}


@pytest.mark.django_db
def test_generate_team_shifts_success(api_client, manager_team):
    url = f"/api/teams/{manager_team.id}/shifts/generate"

    with patch("api.shifts.shift_gestion.views.generate_occurrences_for_window", return_value={"created": 3}):
        response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"created": 3}


@pytest.mark.django_db
def test_generate_team_shifts_invalid_days(api_client, manager_team):
    url = f"/api/teams/{manager_team.id}/shifts/generate?days=0"
    response = api_client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_list_user_shifts_window(api_client, manager_user):
    user_id = manager_user.id
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)
    url = f"/api/users/{user_id}/shifts/list"

    shift_obj = MagicMock()

    with patch_manager_attr(shift_views.UserManager, "get_user_by_id", MagicMock(return_value=manager_user)), \
         patch.object(shift_views.ShiftManager, "check_query_param_element_str", side_effect=lambda request, name: request.query_params.get(name)), \
         patch_manager_attr(shift_views.ShiftManager, "list_shifts_by_user_id_and_date", MagicMock(return_value=[shift_obj])), \
         patch_manager_attr(shift_views.ShiftManager, "check_db_return", MagicMock(return_value=[{"id": 99}])):
        response = api_client.get(url, {"from": start.isoformat(), "to": end.isoformat()})

    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["results"] == [{"id": 99}]


@pytest.mark.django_db
def test_list_user_shifts_window_invalid_range(api_client, manager_user):
    user_id = manager_user.id
    now = datetime.now(timezone.utc)
    url = f"/api/users/{user_id}/shifts/list"

    with patch_manager_attr(shift_views.UserManager, "get_user_by_id", MagicMock(return_value=manager_user)), \
         patch.object(shift_views.ShiftManager, "check_query_param_element_str", side_effect=lambda request, name: request.query_params.get(name)):
        response = api_client.get(url, {"from": now.isoformat(), "to": now.isoformat()})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_team_calendar_view(api_client, manager_team):
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)
    url = f"/api/teams/{manager_team.id}/calendar"

    with patch.object(shift_views.ShiftManager, "check_query_param_element_str", side_effect=lambda request, name: request.query_params.get(name)), \
         patch_manager_attr(shift_views.ShiftManager, "list_shifts_by_team_id", MagicMock(return_value=[MagicMock()])), \
         patch_manager_attr(shift_views.ShiftManager, "check_db_return", MagicMock(return_value=[{"id": 1}])):
        response = api_client.get(url, {"from": start.isoformat(), "to": end.isoformat()})

    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["results"] == [{"id": 1}]
