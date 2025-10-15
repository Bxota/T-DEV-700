# tests/integration/test_team_views.py
import datetime as dt
from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken

from db_manager.models import Users, Teams, Roles


class BaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Données communes
        self.team_a = Teams.objects.create(name="Team A")
        self.team_b = Teams.objects.create(name="Team B")

        self.role_manager = Roles.objects.create(name="manager")
        self.role_user = Roles.objects.create(name="employee")

        self.user = Users.objects.create_user(
            email="user@example.com",
            password="pass",
            first_name="U",
            last_name="Ser",
            team=self.team_a,
            role=self.role_user,
        )
        self.manager = Users.objects.create_user(
            email="manager@example.com",
            password="pass",
            first_name="Mana",
            last_name="Ger",
            team=self.team_a,
            role=self.role_manager,
        )

        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.manager_token = str(RefreshToken.for_user(self.manager).access_token)

        self.base_team_url = "/api/teams/"

    def auth_as(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class TestTeamCollection(BaseAPITest):
    @patch("api.teams.views.TeamManager.list_teams")
    def test_list_teams_ok(self, mock_list):
        # La vue renvoie directement {"teams": ...} sans sérialisation additionnelle
        mock_list.return_value = [{"id": self.team_a.id, "name": self.team_a.name},
                                  {"id": self.team_b.id, "name": self.team_b.name}]

        self.auth_as(self.user_token)
        resp = self.client.get(self.base_team_url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("teams", resp.data)
        self.assertEqual(len(resp.data["teams"]), 2)
        mock_list.assert_called_once()

    @patch("api.teams.views.TeamManager.create_team")
    @patch("api.teams.views.TeamManager.check_if_db_element_with_name_exist")
    @patch("api.teams.views.TeamManager.check_body_element")
    @patch("api.teams.views.TeamManager.check_db_return")
    def test_create_team_ok(self, mock_check_db_return, mock_check_name_exist, mock_check_body, mock_create):
        self.auth_as(self.manager_token)
        mock_check_body.return_value = "New Team"

        # create_team -> instance Teams (au moins .id/.name)
        team_inst = Teams.objects.create(name="placeholder")
        team_inst.name = "New Team"
        mock_create.return_value = team_inst

        # check_db_return -> dict sérialisé
        mock_check_db_return.return_value = {"id": 999, "name": "New Team"}

        resp = self.client.post(self.base_team_url, {"name": "New Team"}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("team", resp.data)
        self.assertEqual(resp.data["team"]["name"], "New Team")

        mock_check_body.assert_called_once()  # validation body "name"
        mock_check_name_exist.assert_called_once()  # unicité
        mock_create.assert_called_once()
        mock_check_db_return.assert_called_once()

    @patch("api.teams.views.TeamManager.check_body_element")
    def test_create_team_missing_name(self, mock_check_body):
        self.auth_as(self.manager_token)
        exc = APIException({"error": "name field is required."})
        exc.status_code = 400
        mock_check_body.side_effect = exc

        resp = self.client.post(self.base_team_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "name field is required.")

    def test_create_team_forbidden_without_manager_permission(self):
        self.auth_as(self.user_token)  # simple employé -> 403
        resp = self.client.post(self.base_team_url, {"name": "X"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch("api.teams.views.TeamManager.check_if_db_element_with_name_exist")
    def test_create_team_conflict_name(self, mock_check_name_exist):
        self.auth_as(self.manager_token)
        exc = APIException({"error": "teams with this name already exists."})
        exc.status_code = 400
        mock_check_name_exist.side_effect = exc

        resp = self.client.post(self.base_team_url, {"name": "Team A"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "teams with this name already exists.")


class TestTeamDetail(BaseAPITest):
    @patch("api.teams.views.TeamManager.get_team_by_id")
    @patch("api.teams.views.TeamManager.check_db_return")
    @patch("api.teams.views.TeamManager.check_db_element_exist")
    def test_get_team_ok(self, mock_check_exist, mock_check_db_return, mock_get):
        # La vue appelle check_db_element_exist puis get_team_by_id puis check_db_return
        mock_check_exist.return_value = self.team_a

        # get_team_by_id -> instance
        mock_get.return_value = self.team_a

        # check_db_return -> dict
        mock_check_db_return.return_value = {"id": self.team_a.id, "name": self.team_a.name}

        self.auth_as(self.user_token)
        url = f"{self.base_team_url}{self.team_a.id}/"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("team", resp.data)
        self.assertEqual(resp.data["team"]["id"], self.team_a.id)

        mock_check_exist.assert_called_once()
        mock_get.assert_called_once()
        mock_check_db_return.assert_called_once()

    @patch("api.teams.views.TeamManager.check_db_element_exist")
    def test_get_team_not_found(self, mock_check_exist):
        exc = APIException({"error": "teams not found."})
        exc.status_code = 400
        mock_check_exist.side_effect = exc

        self.auth_as(self.user_token)
        url = f"{self.base_team_url}9999/"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "teams not found.")

    @patch("api.teams.views.TeamManager.update_team")
    @patch("api.teams.views.TeamManager.check_db_element_exist")
    @patch("api.teams.views.TeamManager.check_body_element")
    def test_update_team_ok(self, mock_check_body, mock_check_exist, mock_update):
        self.auth_as(self.manager_token)
        mock_check_body.return_value = "Renamed"
        mock_check_exist.return_value = self.team_a

        new_inst = Teams.objects.create(name="tmp")
        new_inst.name = "Renamed"
        mock_update.return_value = new_inst

        url = f"{self.base_team_url}{self.team_a.id}/"
        resp = self.client.put(url, {"name": "Renamed"}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("is_updated"))
        self.assertEqual(resp.data.get("new_name"), "Renamed")

    def test_update_team_forbidden_without_manager_permission(self):
        self.auth_as(self.user_token)
        url = f"{self.base_team_url}{self.team_a.id}/"
        resp = self.client.put(url, {"name": "New"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch("api.teams.views.TeamManager.check_body_element")
    def test_update_team_validation_missing_name(self, mock_check_body):
        self.auth_as(self.manager_token)
        exc = APIException({"error": "name field is required."})
        exc.status_code = 400
        mock_check_body.side_effect = exc

        url = f"{self.base_team_url}{self.team_a.id}/"
        resp = self.client.put(url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "name field is required.")

    @patch("api.teams.views.TeamManager.update_team")
    @patch("api.teams.views.TeamManager.check_db_element_exist")
    @patch("api.teams.views.TeamManager.check_body_element")
    def test_update_team_service_error(self, mock_check_body, mock_check_exist, mock_update):
        self.auth_as(self.manager_token)
        mock_check_body.return_value = "NewName"
        mock_check_exist.return_value = self.team_a

        exc = APIException({"error": "update failed"})
        exc.status_code = 400
        mock_update.side_effect = exc

        url = f"{self.base_team_url}{self.team_a.id}/"
        resp = self.client.put(url, {"name": "NewName"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "update failed")

    @patch("api.teams.views.TeamManager.delete_team")
    @patch("api.teams.views.TeamManager.check_db_element_exist")
    def test_delete_team_ok(self, mock_check_exist, mock_delete):
        self.auth_as(self.manager_token)
        mock_check_exist.return_value = self.team_a
        mock_delete.return_value = True

        url = f"{self.base_team_url}{self.team_a.id}/"
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("is_deleted"))
        mock_delete.assert_called_once()

    def test_delete_team_forbidden_without_manager_permission(self):
        self.auth_as(self.user_token)
        url = f"{self.base_team_url}{self.team_a.id}/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @patch("api.teams.views.TeamManager.check_db_element_exist")
    def test_delete_team_not_found(self, mock_check_exist):
        self.auth_as(self.manager_token)
        exc = APIException({"error": "teams not found."})
        exc.status_code = 400
        mock_check_exist.side_effect = exc

        url = f"{self.base_team_url}9999/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "teams not found.")


class TestTeamReports(BaseAPITest):
    @patch("api.teams.views.TeamManager.generate_team_kpi_report")
    @patch("api.teams.views.UserManager.get_users_by_team_id")
    @patch("api.teams.views.TeamManager.get_team_by_id")
    def test_get_team_reports_ok(self, mock_get_team, mock_get_users, mock_generate):
        # Endpoint protégé par HasTeamTagPermission → se connecter en manager
        self.auth_as(self.manager_token)

        # team renvoyée par le service
        mock_get_team.return_value = self.team_a
        # membres renvoyés (peu importe le format, c’est consommé par generate_team_kpi_report)
        mock_get_users.return_value = MagicMock(name="members_qs")
        # rapport renvoyé par le service (dict)
        mock_generate.return_value = {"lateness_rate": 12.5, "members": 3}

        url = f"/api/teams/{self.team_a.id}/reports/"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Le contrôleur enrichit le dict
        self.assertEqual(resp.data["team_name"], self.team_a.name)
        self.assertEqual(resp.data["team_id"], self.team_a.id)
        self.assertEqual(resp.data["lateness_rate"], 12.5)

        mock_get_team.assert_called_once_with(self.team_a.id)
        mock_get_users.assert_called_once_with(self.team_a.id)
        mock_generate.assert_called_once()

    def test_get_team_reports_forbidden_without_manager_permission(self):
        self.auth_as(self.user_token)
        url = f"/api/teams/{self.team_a.id}/reports/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)