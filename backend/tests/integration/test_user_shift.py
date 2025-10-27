# tests/test_user_shift_views.py
import datetime as dt
from unittest.mock import patch, MagicMock

from django.utils import timezone
from django.utils.timezone import make_aware
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import APIException

from db_manager.models import Users, Shifts, Roles, Teams

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

    def auth_as(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class TestUserShiftCollection(BaseAPITest):
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

        exc = APIException({"error": "Overlap"})
        exc.status_code = 400
        mock_create.side_effect = exc

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
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/9999/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "shifts not found.")

    @patch("api.shifts.views.ShiftManager.get_shift_by_id")
    def test_get_shift_user_mismatch(self, mock_get):
        other_user = Users.objects.create_user(
            email="other@example.com", password="pass", role=self.role_user, team=self.team
        )
        shift = self._make_shift(user=other_user)
        mock_get.return_value = shift

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "This shift does not belong to this user.")

    def test_update_shift_validation(self):
        shift = self._make_shift()
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"

        self.auth_as(self.manager_token)

        # missing start_time
        resp = self.client.put(url, {"end_time": iso(make_aware(dt.datetime.now()))}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "start_time field is required.")

        # missing end_time
        resp = self.client.put(url, {"start_time": iso(make_aware(dt.datetime.now()))}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "end_time field is required.")

    @patch("api.shifts.views.ShiftManager.check_valid_shift_interval")
    @patch("api.shifts.views.ShiftManager.update_shift")
    def test_update_shift_ok(self, mock_update, mock_check_valid):
        shift = self._make_shift()
        fake_updated = MagicMock(spec=Shifts)
        fake_updated.id = shift.id
        mock_update.return_value = fake_updated
        mock_check_valid.return_value = True

        self.auth_as(self.manager_token)

        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        start = iso(make_aware(dt.datetime.now()))
        end = iso(make_aware(dt.datetime.now() + dt.timedelta(hours=3)))

        resp = self.client.put(url, {"start_time": start, "end_time": end}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("is_updated"))

    @patch("api.shifts.views.ShiftManager.update_shift")
    def test_update_shift_service_error(self, mock_update):
        shift = self._make_shift()
        mock_update.side_effect = APIException({"error": "Shift time interval overlaps with an existing shift."}, 400)

        self.auth_as(self.manager_token)

        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        start = iso(make_aware(dt.datetime.now()))
        end = iso(make_aware(dt.datetime.now() + dt.timedelta(hours=3)))

        resp = self.client.put(url, {"start_time": start, "end_time": end}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "Shift time interval overlaps with an existing shift.")

    @patch("api.shifts.views.ShiftManager.delete_shift")
    def test_delete_shift_ok_with_manager_permission(self, mock_delete):
        # DELETE vérifie d’abord en base le lien user↔shift puis appelle service
        shift = self._make_shift()
        mock_delete.return_value = True

        self.auth_as(self.manager_token)  # besoin de IsTeamManager
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
        other = Users.objects.create_user(
            email="x@example.com", password="pass", role=self.role_user, team=self.team
        )
        shift = self._make_shift(user=other)

        self.auth_as(self.manager_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/"
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("error"), "This shift does not belong to this user.")
        
    @patch("api.shifts.views.ShiftManager.check_in")
    def test_check_in_ok(self, mock_check_in):
        shift = self._make_shift()
        shift.real_start_time = None
        mock_check_in.return_value = shift

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/check-in/"
        start_time = iso(make_aware(dt.datetime.now()))
        resp = self.client.post(url, {"start_time": start_time}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("is_check_in"))
        self.assertIn("shift", resp.data)
        mock_check_in.assert_called_once_with(shift_id=shift.id, start_time=start_time)

    def test_check_in_missing_start_time(self):
        shift = self._make_shift()
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/check-in/"
        resp = self.client.post(url, {}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "start_time field is required.")

    def test_check_in_already_started(self):
        shift = self._make_shift()
        shift.real_start_time = make_aware(dt.datetime.now())
        shift.save()

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/check-in/"
        start_time = iso(make_aware(dt.datetime.now()))
        resp = self.client.post(url, {"start_time": start_time}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "shifts already has a real_start_time element")
        
    def test_check_in_user_not_found(self):
        shift = self._make_shift()
        shift.real_start_time = None

        self.auth_as(self.user_token)
        url = f"/api/users/9999/shifts/{shift.id}/check-in/"
        start_time = iso(make_aware(dt.datetime.now()))
        resp = self.client.post(url, {"start_time": start_time}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "users not found.")
        
    def test_check_in_shift_not_found(self):
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/9999/check-in/"
        start_time = iso(make_aware(dt.datetime.now()))
        resp = self.client.post(url, {"start_time": start_time}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "shifts not found.")
        
    @patch("api.shifts.views.ShiftManager.check_out")
    def test_check_out_ok(self, mock_check_out):
        shift = self._make_shift()
        shift.real_start_time = make_aware(dt.datetime.now())
        shift.real_end_time = None
        shift.save()

        mock_check_out.return_value = shift
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/check-out/"
        end_time = iso(make_aware(dt.datetime.now() + dt.timedelta(hours=2)))
        resp = self.client.post(url, {"end_time": end_time}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("is_check_out"))
        self.assertIn("shift", resp.data)
        mock_check_out.assert_called_once_with(shift_id=shift.id, end_time=end_time)

    def test_check_out_missing_end_time(self):
        shift = self._make_shift()
        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/check-out/"
        resp = self.client.post(url, {}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "end_time field is required.")

    def test_check_out_without_check_in(self):
        shift = self._make_shift()
        shift.real_start_time = None
        shift.real_end_time = None
        shift.save()

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/check-out/"
        end_time = iso(make_aware(dt.datetime.now()))
        resp = self.client.post(url, {"end_time": end_time}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "shifts doesn't has a real_start_time element")

    def test_check_out_already_ended(self):
        shift = self._make_shift()
        shift.real_start_time = make_aware(dt.datetime.now())
        shift.real_end_time = make_aware(dt.datetime.now() + dt.timedelta(hours=1))
        shift.save()

        self.auth_as(self.user_token)
        url = f"/api/users/{self.user.id}/shifts/{shift.id}/check-out/"
        end_time = iso(make_aware(dt.datetime.now() + dt.timedelta(hours=2)))
        resp = self.client.post(url, {"end_time": end_time}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "shifts already has a real_end_time element")