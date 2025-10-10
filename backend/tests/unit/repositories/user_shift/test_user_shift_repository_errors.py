# tests/repositories/test_shift_repository_exceptions.py

from datetime import datetime, timezone
from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock

from db_manager.repositories.shifts_repository import ShiftRepository


TARGET = "db_manager.repositories.shifts_repository.Shifts"


class ShiftRepositoryExceptionTests(SimpleTestCase):
    # ---------- get_shifts ----------
    @patch(TARGET)
    def test_get_shifts_generic_exception(self, ShiftsMock):
        # order_by() lève une exception
        ShiftsMock.objects.order_by.side_effect = Exception("boom-order-by")

        res = ShiftRepository.get_shifts()
        assert res == {"error": "boom-order-by"}

    # ---------- get_shifts_by_user_id ----------
    @patch(TARGET)
    def test_get_shifts_by_user_id_generic_exception(self, ShiftsMock):
        ShiftsMock.objects.filter.side_effect = Exception("boom-filter")

        res = ShiftRepository.get_shifts_by_user_id(user_id=1)
        assert res == {"error": "boom-filter"}

    # ---------- create_shift ----------
    @patch(TARGET)
    def test_create_shift_generic_exception_on_create(self, ShiftsMock):
        # Pas de doublon → exists() == False
        qsmock = MagicMock()
        qsmock.exists.return_value = False
        ShiftsMock.objects.filter.return_value = qsmock

        # create() lève une exception
        ShiftsMock.objects.create.side_effect = Exception("db-create-failed")

        user = object()
        start = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc)

        res = ShiftRepository.create_shift(user=user, start_time=start, end_time=end)
        assert res == {"error": "db-create-failed"}

    @patch(TARGET)
    def test_create_shift_generic_exception_on_filter(self, ShiftsMock):
        # filter() lui-même lève une exception (avant even exists())
        ShiftsMock.objects.filter.side_effect = Exception("filter-broken")

        user = object()
        start = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc)

        res = ShiftRepository.create_shift(user=user, start_time=start, end_time=end)
        assert res == {"error": "filter-broken"}

    # ---------- get_shift_by_id ----------
    @patch(TARGET)
    def test_get_shift_by_id_generic_exception(self, ShiftsMock):
        ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})
        ShiftsMock.objects.get.side_effect = Exception("weird-db-error")

        res = ShiftRepository.get_shift_by_id(123)
        assert res == {"error": "weird-db-error"}

    # ---------- update_shift ----------
    @patch(TARGET)
    def test_update_shift_generic_exception_on_save(self, ShiftsMock):
        # <<< IMPORTANT : définir l'exception >>>
        ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})

        # get() renvoie un objet dont save() lève
        shift_inst = MagicMock()
        shift_inst.save.side_effect = Exception("io-error-on-save")
        ShiftsMock.objects.get.return_value = shift_inst

        start = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

        res = ShiftRepository.update_shift(shift_id=1, start_time=start, end_time=end)
        assert res == {"error": "io-error-on-save"}

    @patch(TARGET)
    def test_update_shift_generic_exception_on_get(self, ShiftsMock):
        ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})

        ShiftsMock.objects.get.side_effect = Exception("boom-on-get")

        start = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

        res = ShiftRepository.update_shift(shift_id=1, start_time=start, end_time=end)
        assert res == {"error": "boom-on-get"}
        
    # ---------- delete_shift ----------
    @patch(TARGET)
    def test_delete_shift_generic_exception_on_delete(self, ShiftsMock):
        ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})

        shift_inst = MagicMock()
        shift_inst.delete.side_effect = Exception("cannot-delete")
        ShiftsMock.objects.get.return_value = shift_inst

        res = ShiftRepository.delete_shift(1)
        assert res == {"error": "cannot-delete"}
    
    @patch(TARGET)
    def test_delete_shift_generic_exception_on_get(self, ShiftsMock):
        # Rendre l’exception catchable
        ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})

        # Force une exception générique sur get()
        ShiftsMock.objects.get.side_effect = Exception("boom-on-get-delete")

        res = ShiftRepository.delete_shift(1)
        self.assertEqual(res, {"error": "boom-on-get-delete"})