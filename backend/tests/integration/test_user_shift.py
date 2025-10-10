# tests/test_user_shift_views.py
import datetime as dt
from unittest.mock import patch, MagicMock

from django.utils.timezone import make_aware
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from db_manager.models import Users, Shifts, Roles, Teams  # adapte si tes noms diffèrent
from rest_framework_simplejwt.tokens import RefreshToken


def iso(dt_obj):
    return dt_obj.isoformat().replace("+00:00", "Z")


class BaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Données communes
        self.team = Teams.objects.create(name="Team A")
        self.role_manager = Roles.objects.create(name="manager")
        self.role_user = Roles.objects.create(name="employee")

        self.user = Users.objects.create_user(
            email="user@example.com",
            password="pass",
            first_name="U",
            last_name="Ser",
            team=self.team,
            role=self.role_user,
        )
        self.manager = Users.objects.create_user(
            email="manager@example.com",
            password="pass",
            first_name="Mana",
            last_name="Ger",
            team=self.team,
            role=self.role_manager,
        )

        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.manager_token = str(RefreshToken.for_user(self.manager).access_token)

        self.base_user_url = f"/api/users/{self.user.id}/shifts/"
        # On créera un shift concret en base quand nécessaire et on formera l’URL détail:
        # f"/api/users/{self.user.id}/shifts/{shift.id}/"

    def auth_as(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class TestUserShiftCollection(BaseAPITest):
    @patch("api.shifts.views.ShiftManager.list_shifts_by_user_id")  # adapte le path exact du module
    def test_list_shifts_by_user_ok(self, mock_list):
        # Arrange
        # La vue renvoie directement {"shifts": <retour>} sans sérialiser donc on simule une liste de dicts
        now = make_aware(dt.datetime.now())
        mock_list.return_value = [
            {
                "id": 101,
                "user": self.user.id,
                "start_time": iso(now),
                "end_time": iso(now + dt.timedelta(hours=2)),
            }
        ]

        self.auth_as(self.user_token)
        # Act
        resp = self.client.get(self.base_user_url)

        # Assert
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("shifts", resp.data)
        self.assertEqual(len(resp.data["shifts"]), 1)
        mock_list.assert_called_once_with(self.user.id)

    def test_create_shift_validation_missing_start(self):
        self.auth_as(self.user_token)
        payload = {"end_time": iso(make_aware(dt.datetime.now() + dt.timedelta(hours=1)))}
        resp = self.client.post(self.base_user_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "start_time field is required.")

    def test_create_shift_validation_missing_end(self):
        self.auth_as(self.user_token)
        payload = {"start_time": iso(make_aware(dt.datetime.now()))}
        resp = self.client.post(self.base_user_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "end_time field is required.")

    @patch("api.shifts.views.ShiftManager.create_shift")
    def test_create_shift_ok(self, mock_create):
        self.auth_as(self.user_token)
        start = make_aware(dt.datetime.now())
        end = start + dt.timedelta(hours=2)

        # Simule un objet Shifts avec un id
        fake_shift = MagicMock(spec=Shifts)
        fake_shift.id = 777
        mock_create.return_value = fake_shift

        payload = {"start_time": iso(start), "end_time": iso(end)}
        resp = self.client.post(self.base_user_url, payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data.get("is_created"))
        self.assertEqual(resp.data.get("id"), 777)
        mock_create.assert_called_once()
        # Vérifie que la vue passe bien user + start/end (string ISO)
        args, kwargs = mock_create.call_args
        self.assertEqual(kwargs["user"].id, self.user.id)
        self.assertEqual(kwargs["start_time"], payload["start_time"])
        self.assertEqual(kwargs["end_time"], payload["end_time"])

    @patch("api.shifts.views.ShiftManager.create_shift")
    def test_create_shift_service_error(self, mock_create):
        self.auth_as(self.user_token)
        start = iso(make_aware(dt.datetime.now()))
        end = iso(make_aware(dt.datetime.now() + dt.timedelta(hours=2)))
        mock_create.return_value = {"error": "Overlap"}

        resp = self.client.post(self.base_user_url, {"start_time": start, "end_time": end}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "Overlap")


class TestUserShiftDetail(BaseAPITest):
    def _make_shift(self, user=None, start=None, end=None):
        user = user or self.user
        start = start or make_aware(dt.datetime.now())
        end = end or (start + dt.timedelta(hours=2))
        return Shifts.objects.create(user=user, start_time=start, end_time=end)

    @patch("api.shifts.views.ShiftManager.get_shift_by_id")
    def test_get_shift_ok(self, mock_get):
        # Arrange: un vrai shift en base (utilisé pour la cohérence serializer et user link check)
        shift = self._make_shift()
        mock_get.return_value = shift

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("shift", resp.data)
        self.assertEqual(resp.data["shift"]["id"], shift.id)

    @patch("api.shifts.views.ShiftManager.get_shift_by_id")
    def test_get_shift_service_error(self, mock_get):
        mock_get.return_value = {"error": "Shift not found."}
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/9999/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "Shift not found.")

    @patch("api.shifts.views.ShiftManager.get_shift_by_id")
    def test_get_shift_user_mismatch(self, mock_get):
        # shift appartenant à un autre user
        other_user = Users.objects.create_user(
            email="other@example.com", password="pass", role=self.role_user, team=self.team
        )
        shift = self._make_shift(user=other_user)
        mock_get.return_value = shift

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "User and Shift not linked.")

    def test_update_shift_validation(self):
        shift = self._make_shift()
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"

        # missing start_time
        resp = self.client.post(url, {"end_time": iso(make_aware(dt.datetime.now()))}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "start_time field is required.")

        # missing end_time
        resp = self.client.post(url, {"start_time": iso(make_aware(dt.datetime.now()))}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "end_time field is required.")

    @patch("api.shifts.views.ShiftManager.update_shift")
    def test_update_shift_ok(self, mock_update):
        shift = self._make_shift()
        fake_updated = MagicMock(spec=Shifts)
        fake_updated.id = shift.id
        mock_update.return_value = fake_updated

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        start = iso(make_aware(dt.datetime.now()))
        end = iso(make_aware(dt.datetime.now() + dt.timedelta(hours=3)))

        resp = self.client.post(url, {"start_time": start, "end_time": end}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("is_updated"))
        self.assertEqual(resp.data.get("id"), shift.id)

    @patch("api.shifts.views.ShiftManager.update_shift")
    def test_update_shift_service_error(self, mock_update):
        shift = self._make_shift()
        mock_update.return_value = {"error": "Overlap"}
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        start = iso(make_aware(dt.datetime.now()))
        end = iso(make_aware(dt.datetime.now() + dt.timedelta(hours=3)))

        resp = self.client.post(url, {"start_time": start, "end_time": end}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "Overlap")

    @patch("api.shifts.views.ShiftManager.delete_shift")
    def test_delete_shift_ok_with_manager_permission(self, mock_delete):
        # DELETE vérifie d’abord en base le lien user↔shift puis appelle service
        shift = self._make_shift()
        mock_delete.return_value = True

        self.auth_as(self.manager_token)  # besoin de HasTeamTagPermission
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("is_deleted"))
        mock_delete.assert_called_once_with(shift_id=shift.id)

    def test_delete_shift_forbidden_without_manager_permission(self):
        shift = self._make_shift()

        self.auth_as(self.user_token)  # simple employé -> 403 attendu
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_shift_user_mismatch(self):
        # Si le shift n’appartient pas au user de l’URL, la vue retourne un dict {"error": ...}
        other = Users.objects.create_user(
            email="x@example.com", password="pass", role=self.role_user, team=self.team
        )
        shift = self._make_shift(user=other)

        self.auth_as(self.manager_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "User and Shift not linked.")