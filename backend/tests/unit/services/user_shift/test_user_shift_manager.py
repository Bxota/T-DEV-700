from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase

from api.shifts.service import ShiftManager

class ShiftManagerTests(SimpleTestCase):
    def setUp(self):
        # Données communes
        self.user = MagicMock()  # Pas besoin d'un vrai Users, on mock
        self.start = datetime(2025, 1, 1, 9, 0, 0)
        self.end = self.start + timedelta(hours=2)
        self.shift_id = 42
        self.user_id = 7

    @patch("api.shifts.service.ShiftRepository")
    def test_list_shifts_delegates_and_returns(self, repo_mock):
        expected = [{"id": 1}, {"id": 2}]
        repo_mock.get_shifts.return_value = expected

        result = ShiftManager.list_shifts()

        repo_mock.get_shifts.assert_called_once_with()
        self.assertEqual(result, expected)

    @patch("api.shifts.service.ShiftRepository")
    def test_list_shifts_by_user_id_delegates_and_returns(self, repo_mock):
        expected = [{"id": 10, "user_id": self.user_id}]
        repo_mock.get_shifts_by_user_id.return_value = expected

        # Appel via la classe (le method n'est pas décoré @staticmethod mais ça marche via la classe)
        result = ShiftManager.list_shifts_by_user_id(self.user_id)

        repo_mock.get_shifts_by_user_id.assert_called_once_with(user_id=self.user_id)
        self.assertEqual(result, expected)

    @patch("api.shifts.service.ShiftRepository")
    def test_create_shift_delegates_and_returns(self, repo_mock):
        expected = {"id": 123, "user": "u", "start": self.start, "end": self.end}
        repo_mock.create_shift.return_value = expected

        result = ShiftManager.create_shift(user=self.user, start_time=self.start, end_time=self.end)

        repo_mock.create_shift.assert_called_once_with(user=self.user, start_time=self.start, end_time=self.end)
        self.assertEqual(result, expected)

    @patch("api.shifts.service.ShiftRepository")
    def test_get_shift_by_id_delegates_and_returns(self, repo_mock):
        expected = {"id": self.shift_id}
        repo_mock.get_shift_by_id.return_value = expected

        result = ShiftManager.get_shift_by_id(self.shift_id)

        repo_mock.get_shift_by_id.assert_called_once_with(self.shift_id)
        self.assertEqual(result, expected)

    @patch("api.shifts.service.ShiftRepository")
    def test_update_shift_delegates_and_returns(self, repo_mock):
        expected = {"id": self.shift_id, "start": self.start, "end": self.end}
        repo_mock.update_shift.return_value = expected

        result = ShiftManager.update_shift(shift_id=self.shift_id, start_time=self.start, end_time=self.end)

        repo_mock.update_shift.assert_called_once_with(
            shift_id=self.shift_id, start_time=self.start, end_time=self.end
        )
        self.assertEqual(result, expected)

    @patch("api.shifts.service.ShiftRepository")
    def test_delete_shift_delegates_and_returns(self, repo_mock):
        expected = {"deleted": True}
        repo_mock.delete_shift.return_value = expected

        result = ShiftManager.delete_shift(self.shift_id)

        repo_mock.delete_shift.assert_called_once_with(self.shift_id)
        self.assertEqual(result, expected)

    @patch("api.shifts.service.ShiftRepository")
    def test_exceptions_from_repository_are_propagated(self, repo_mock):
        repo_mock.get_shift_by_id.side_effect = ValueError("boom")

        with self.assertRaises(ValueError) as ctx:
            ShiftManager.get_shift_by_id(self.shift_id)

        self.assertIn("boom", str(ctx.exception))