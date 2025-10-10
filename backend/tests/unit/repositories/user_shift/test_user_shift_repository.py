# tests/repositories/test_shift_repository.py

from datetime import datetime, timedelta, timezone
from django.test import TestCase

from db_manager.models import Users, Teams, Shifts
from db_manager.repositories.shifts_repository import ShiftRepository


class ShiftRepositoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Création de données communes
        cls.team = Teams.objects.create(name="Team A")
        cls.user_a = Users.objects.create(email="a@example.com", first_name="A", last_name="AA", team=cls.team)
        cls.user_b = Users.objects.create(email="b@example.com", first_name="B", last_name="BB", team=cls.team)

    # ---------- Helpers ----------
    def make_shift(self, user, start, end):
        return Shifts.objects.create(user=user, start_time=start, end_time=end)

    def make_datetime(self, hour=9, minute=0):
        return datetime(2025, 1, 1, hour, minute, 0, tzinfo=timezone.utc)

    # ---------- get_shifts ----------
    def test_get_shifts_returns_list_of_dicts(self):
        s1 = self.make_shift(self.user_a, self.make_datetime(9), self.make_datetime(11))
        s2 = self.make_shift(self.user_b, self.make_datetime(12), self.make_datetime(14))

        res = ShiftRepository.get_shifts()

        self.assertIsInstance(res, list)
        self.assertEqual([r["id"] for r in res], [s1.id, s2.id])
        self.assertTrue(all(isinstance(r, dict) and set(r.keys()) == {"id"} for r in res))

    # ---------- get_shifts_by_user_id ----------
    def test_get_shifts_by_user_id_returns_list_of_instances(self):
        s1 = self.make_shift(self.user_a, self.make_datetime(9), self.make_datetime(11))
        _ = self.make_shift(self.user_b, self.make_datetime(9), self.make_datetime(11))

        res = ShiftRepository.get_shifts_by_user_id(self.user_a.id)

        self.assertIsInstance(res, list)
        self.assertTrue(all(isinstance(s, Shifts) for s in res))
        self.assertEqual([s.id for s in res], [s1.id])

    # ---------- create_shift ----------
    def test_create_shift_success(self):
        start, end = self.make_datetime(8), self.make_datetime(10)
        res = ShiftRepository.create_shift(self.user_a, start, end)

        self.assertIsInstance(res, Shifts)
        self.assertEqual(res.user_id, self.user_a.id)
        self.assertEqual(res.start_time, start)
        self.assertEqual(res.end_time, end)

    def test_create_shift_duplicate_returns_error(self):
        start, end = self.make_datetime(8), self.make_datetime(10)
        self.make_shift(self.user_a, start, end)

        res = ShiftRepository.create_shift(self.user_a, start, end)

        self.assertEqual(res, {"error": "Shift with this user and start/end time already exists."})

    # ---------- get_shift_by_id ----------
    def test_get_shift_by_id_found(self):
        s = self.make_shift(self.user_a, self.make_datetime(9), self.make_datetime(11))
        res = ShiftRepository.get_shift_by_id(s.id)

        self.assertIsInstance(res, Shifts)
        self.assertEqual(res.id, s.id)

    def test_get_shift_by_id_not_found(self):
        res = ShiftRepository.get_shift_by_id(9999)
        self.assertEqual(res, {"error": "Shift not found."})

    # ---------- update_shift ----------
    def test_update_shift_success(self):
        s = self.make_shift(self.user_a, self.make_datetime(9), self.make_datetime(11))
        new_start, new_end = self.make_datetime(10), self.make_datetime(12)

        res = ShiftRepository.update_shift(s.id, new_start, new_end)

        self.assertIsInstance(res, Shifts)
        self.assertEqual(res.start_time, new_start)
        self.assertEqual(res.end_time, new_end)

        s.refresh_from_db()
        self.assertEqual(s.start_time, new_start)
        self.assertEqual(s.end_time, new_end)

    def test_update_shift_not_found(self):
        res = ShiftRepository.update_shift(9999, self.make_datetime(10), self.make_datetime(12))
        self.assertEqual(res, {"error": "Shift not found."})

    # ---------- delete_shift ----------
    def test_delete_shift_success(self):
        s = self.make_shift(self.user_b, self.make_datetime(13), self.make_datetime(15))

        res = ShiftRepository.delete_shift(s.id)

        self.assertTrue(res)
        self.assertFalse(Shifts.objects.filter(id=s.id).exists())

    def test_delete_shift_not_found(self):
        res = ShiftRepository.delete_shift(9999)
        self.assertEqual(res, {"error": "Shift not found."})