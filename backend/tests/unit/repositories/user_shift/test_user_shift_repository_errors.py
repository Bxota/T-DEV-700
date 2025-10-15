# tests/unit/repositories/test_shifts_repository.py
import datetime as dt
from unittest.mock import patch, MagicMock

import pytest
from rest_framework.exceptions import APIException

from db_manager.repositories.shifts_repository import ShiftRepository

TARGET = "db_manager.repositories.shifts_repository.Shifts"


# ---------- get_shifts ----------
@patch(TARGET)
def test_get_shifts_ok(ShiftsMock):
    qs = MagicMock()
    qs.values.return_value = [{"id": 1}, {"id": 2}]
    ShiftsMock.objects.order_by.return_value = qs

    res = ShiftRepository.get_shifts()
    assert res == [{"id": 1}, {"id": 2}]


@patch(TARGET)
def test_get_shifts_exception_returns_apiexception_instance(ShiftsMock):
    ShiftsMock.objects.order_by.side_effect = Exception("boom")

    res = ShiftRepository.get_shifts()
    assert isinstance(res, APIException)
    # DRF enveloppe detail dans ErrorDetail -> cast en str
    assert str(res.detail["error"]) == "internal server error."
    assert str(res.detail["status_code"]) == "500"


# ---------- get_shifts_by_user_id ----------
@patch(TARGET)
def test_get_shifts_by_user_id_ok(ShiftsMock):
    filtered = MagicMock()
    expected = MagicMock(name="ordered_qs")
    filtered.order_by.return_value = expected
    ShiftsMock.objects.filter.return_value = filtered

    res = ShiftRepository.get_shifts_by_user_id(user_id=7)
    assert res is expected
    ShiftsMock.objects.filter.assert_called_once_with(user_id=7)
    filtered.order_by.assert_called_once_with("id")


@patch(TARGET)
def test_get_shifts_by_user_id_exception_raises_apiexception(ShiftsMock):
    ShiftsMock.objects.filter.side_effect = Exception("db down")

    with pytest.raises(APIException) as err:
        ShiftRepository.get_shifts_by_user_id(user_id=7)
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------- get_shifts_by_team_id ----------
@patch(TARGET)
def test_get_shifts_by_team_id_ok(ShiftsMock):
    filtered = MagicMock()
    expected = MagicMock(name="ordered_qs")
    filtered.order_by.return_value = expected
    ShiftsMock.objects.filter.return_value = filtered

    res = ShiftRepository.get_shifts_by_team_id(team_id=3)
    assert res is expected
    ShiftsMock.objects.filter.assert_called_once_with(user__team_id=3)
    filtered.order_by.assert_called_once_with("id")


@patch(TARGET)
def test_get_shifts_by_team_id_exception_raises_apiexception(ShiftsMock):
    ShiftsMock.objects.filter.side_effect = Exception("oops")

    with pytest.raises(APIException) as err:
        ShiftRepository.get_shifts_by_team_id(team_id=3)
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------- create_shift ----------
@patch(TARGET)
def test_create_shift_ok(ShiftsMock):
    shift_inst = MagicMock()
    ShiftsMock.objects.create.return_value = shift_inst

    u = MagicMock()
    start = dt.datetime(2025, 1, 1, 10, 0)
    end = dt.datetime(2025, 1, 1, 12, 0)

    res = ShiftRepository.create_shift(user=u, start_time=start, end_time=end)
    assert res is shift_inst
    ShiftsMock.objects.create.assert_called_once_with(user=u, start_time=start, end_time=end)


@patch(TARGET)
def test_create_shift_exception_raises_apiexception(ShiftsMock):
    ShiftsMock.objects.create.side_effect = Exception("db fail")

    with pytest.raises(APIException) as err:
        ShiftRepository.create_shift(user=MagicMock(), start_time=dt.datetime.now(), end_time=dt.datetime.now())
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------- get_shift_by_id ----------
@patch(TARGET)
def test_get_shift_by_id_ok(ShiftsMock):
    shift_inst = MagicMock()
    ShiftsMock.objects.get.return_value = shift_inst

    res = ShiftRepository.get_shift_by_id(42)
    assert res is shift_inst
    ShiftsMock.objects.get.assert_called_once_with(id=42)


@patch(TARGET)
def test_get_shift_by_id_exception_raises_apiexception(ShiftsMock):
    ShiftsMock.objects.get.side_effect = Exception("nope")

    with pytest.raises(APIException) as err:
        ShiftRepository.get_shift_by_id(42)
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------- update_shift ----------
@patch(TARGET)
def test_update_shift_ok(ShiftsMock):
    shift_inst = MagicMock()
    ShiftsMock.objects.get.return_value = shift_inst

    start = dt.datetime(2025, 1, 1, 10, 0)
    end = dt.datetime(2025, 1, 1, 12, 0)

    res = ShiftRepository.update_shift(shift_id=1, start_time=start, end_time=end)
    assert res is shift_inst
    assert shift_inst.start_time == start
    assert shift_inst.end_time == end
    shift_inst.save.assert_called_once()
    ShiftsMock.objects.get.assert_called_once_with(id=1)


@patch(TARGET)
def test_update_shift_exception_on_get_raises_apiexception(ShiftsMock):
    ShiftsMock.objects.get.side_effect = Exception("boom")

    with pytest.raises(APIException) as err:
        ShiftRepository.update_shift(shift_id=1, start_time=dt.datetime.now(), end_time=dt.datetime.now())
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


@patch(TARGET)
def test_update_shift_exception_on_save_raises_apiexception(ShiftsMock):
    shift_inst = MagicMock()
    shift_inst.save.side_effect = Exception("save failed")
    ShiftsMock.objects.get.return_value = shift_inst

    with pytest.raises(APIException) as err:
        ShiftRepository.update_shift(shift_id=1, start_time=dt.datetime.now(), end_time=dt.datetime.now())
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------- delete_shift ----------
@patch(TARGET)
def test_delete_shift_ok(ShiftsMock):
    shift_inst = MagicMock()
    ShiftsMock.objects.get.return_value = shift_inst

    res = ShiftRepository.delete_shift(shift_id=9)
    assert res is True
    shift_inst.delete.assert_called_once()
    ShiftsMock.objects.get.assert_called_once_with(id=9)


@patch(TARGET)
def test_delete_shift_exception_raises_apiexception(ShiftsMock):
    ShiftsMock.objects.get.side_effect = Exception("boom")

    with pytest.raises(APIException) as err:
        ShiftRepository.delete_shift(shift_id=9)
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------- check_in ----------
@patch(TARGET)
def test_check_in_ok(ShiftsMock):
    shift_inst = MagicMock()
    ShiftsMock.objects.get.return_value = shift_inst

    start = dt.datetime(2025, 1, 1, 10, 5)
    res = ShiftRepository.check_in(shift_id=1, start_time=start)

    assert res is shift_inst
    assert shift_inst.real_start_time == start
    shift_inst.save.assert_called_once()


@patch(TARGET)
def test_check_in_not_found_returns_dict(ShiftsMock):
    # définir l'exception DoesNotExist sur le mock
    ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})
    ShiftsMock.objects.get.side_effect = ShiftsMock.DoesNotExist()

    res = ShiftRepository.check_in(shift_id=1, start_time=dt.datetime.now())
    assert res == {"error": "Shift not found."}


@patch(TARGET)
def test_check_in_generic_exception_returns_error_dict(ShiftsMock):
    shift_inst = MagicMock()
    shift_inst.save.side_effect = Exception("db down")
    ShiftsMock.objects.get.return_value = shift_inst

    res = ShiftRepository.check_in(shift_id=1, start_time=dt.datetime.now())
    assert res == {"error": "db down"}


# ---------- check_out ----------
@patch(TARGET)
def test_check_out_ok(ShiftsMock):
    shift_inst = MagicMock()
    ShiftsMock.objects.get.return_value = shift_inst

    end = dt.datetime(2025, 1, 1, 12, 30)
    res = ShiftRepository.check_out(shift_id=1, end_time=end)

    assert res is shift_inst
    assert shift_inst.real_end_time == end
    shift_inst.save.assert_called_once()


@patch(TARGET)
def test_check_out_generic_exception_returns_error_dict(ShiftsMock):
    ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})

    shift_inst = MagicMock()
    shift_inst.save.side_effect = Exception("save err")
    ShiftsMock.objects.get.return_value = shift_inst

    from db_manager.repositories.shifts_repository import ShiftRepository
    res = ShiftRepository.check_out(shift_id=1, end_time=dt.datetime.now())
    assert res == {"error": "save err"}


@patch(TARGET)
def test_check_in_generic_exception_returns_error_dict(ShiftsMock):
    ShiftsMock.DoesNotExist = type("DoesNotExist", (Exception,), {})

    shift_inst = MagicMock()
    shift_inst.save.side_effect = Exception("db down")
    ShiftsMock.objects.get.return_value = shift_inst

    from db_manager.repositories.shifts_repository import ShiftRepository
    res = ShiftRepository.check_in(shift_id=1, start_time=dt.datetime.now())
    assert res == {"error": "db down"}