from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from api.users import views as user_views
from db_manager.models import Roles, Teams, Users


@pytest.fixture
def manager_setup(db):
    team = Teams.objects.create(name="Team Users")
    role_manager = Roles.objects.create(name="manager")
    role_employee = Roles.objects.create(name="employee")

    manager = Users.objects.create_user(
        email="manager-users@example.com",
        password="pass",
        first_name="Mana",
        last_name="Ger",
        team=team,
        role=role_manager,
    )
    employee = Users.objects.create_user(
        email="emp@example.com",
        password="pass",
        first_name="Emp",
        last_name="Loyee",
        team=team,
        role=role_employee,
    )
    return manager, employee, team


@pytest.fixture
def authed_client(manager_setup):
    manager, _, _ = manager_setup
    client = APIClient()
    client.force_authenticate(user=manager)
    return client


@pytest.mark.django_db
def test_get_user_reports(authed_client, manager_setup):
    manager, employee, _ = manager_setup
    url = f"/api/users/{employee.id}/reports"

    with patch.object(user_views.UserManager, "get_user_by_id", return_value=employee), \
         patch.object(user_views.ShiftManager, "list_shifts_by_user_id", return_value=[]), \
         patch.object(user_views.TeamManager, "generate_user_kpi_report", return_value={"hours": 10}):
        response = authed_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"hours": 10}


@pytest.mark.django_db
def test_user_team_collection_get(authed_client, manager_setup):
    manager, employee, team = manager_setup
    url = f"/api/users/teams/{team.id}/"

    with patch.object(user_views.UserManager, "check_db_element_exist", return_value=team), \
         patch.object(user_views.UserManager, "get_users_by_team_id", return_value=[employee]), \
         patch.object(user_views.UserManager, "check_db_return", return_value=[{"id": employee.id}]):
        response = authed_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"users": [{"id": employee.id}]}


@pytest.mark.django_db
def test_user_team_collection_post(authed_client, manager_setup):
    manager, employee, team = manager_setup
    url = f"/api/users/teams/{team.id}/"
    payload = {"user_id": employee.id}

    with patch.object(user_views.UserManager, "check_db_element_exist", return_value=team), \
         patch.object(user_views.UserManager, "add_user_to_team", return_value=True), \
         patch.object(user_views.UserManager, "check_body_element", side_effect=lambda req, name: req.data[name]):
        response = authed_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"is_added": True}


@pytest.mark.django_db
def test_user_team_collection_delete(authed_client, manager_setup):
    manager, employee, team = manager_setup
    url = f"/api/users/teams/{team.id}/"
    payload = {"user_id": employee.id}

    with patch.object(user_views.UserManager, "check_db_element_exist", return_value=team), \
         patch.object(user_views.UserManager, "delete_user_from_team", return_value=True), \
         patch.object(user_views.UserManager, "check_body_element", side_effect=lambda req, name: req.data[name]):
        response = authed_client.delete(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"is_deleted": True}


@pytest.mark.django_db
def test_user_collection_get(authed_client):
    url = "/api/users/"
    with patch.object(user_views.UserManager, "get_all_users", return_value=[]), \
         patch.object(user_views.UserManager, "check_db_return", return_value=[]):
        response = authed_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"users": []}


@pytest.mark.django_db
def test_user_collection_post(authed_client):
    url = "/api/users/"
    payload = {"email": "new@example.com", "password": "pwd"}

    with patch.object(user_views.UserManager, "check_body_element", side_effect=lambda req, name: req.data[name]), \
         patch.object(user_views.UserManager, "check_if_db_element_with_email_exist", return_value=None), \
         patch.object(user_views.UserManager, "create_user", return_value={"id": 9}):
        response = authed_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {"user": {"id": 9}}


@pytest.mark.django_db
def test_user_detail_get(authed_client):
    url = "/api/users/5/"

    with patch.object(user_views.UserManager, "get_user_by_id", return_value=MagicMock()), \
         patch.object(user_views.UserManager, "check_db_return", return_value={"id": 5}):
        response = authed_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"user": {"id": 5}}


@pytest.mark.django_db
def test_user_detail_put(authed_client):
    url = "/api/users/5/"
    payload = {"email": "up@example.com"}

    with patch.object(user_views.UserManager, "check_db_element_exist", return_value=MagicMock()), \
         patch.object(user_views.UserManager, "check_valid_field_in_kwargs", return_value=None), \
         patch.object(user_views.UserManager, "update_user", return_value=True):
        response = authed_client.put(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"is_updated": True}


@pytest.mark.django_db
def test_user_detail_delete(authed_client):
    url = "/api/users/5/"

    with patch.object(user_views.UserManager, "check_db_element_exist", return_value=MagicMock()), \
         patch.object(user_views.UserManager, "delete_user", return_value=True):
        response = authed_client.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"is_deleted": True}


@pytest.mark.django_db
def test_user_roles_list(authed_client):
    url = "/api/roles/"

    with patch.object(user_views.UserManager, "get_roles", return_value=[]), \
         patch.object(user_views.UserManager, "check_db_return", return_value=[]):
        response = authed_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"roles": []}


@pytest.mark.django_db
def test_get_user_clocks_summary(authed_client, manager_setup):
    _, _, team = manager_setup
    response = authed_client.get(f"/api/users/{team.id}/clocks")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {}
