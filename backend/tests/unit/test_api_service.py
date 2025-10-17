import types
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.http import QueryDict
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError

from api.service import AbstractManager
from db_manager.models import Shifts, Users, Teams, Roles


@pytest.fixture
def rf():
    return APIRequestFactory()


class DummySerializer:
    def __init__(self, obj, many=False):
        self.obj = obj
        self.many = many

    @property
    def data(self):
        if self.many:
            return [self._serialize(item) for item in self.obj]
        return self._serialize(self.obj)

    def _serialize(self, item):
        return getattr(item, "value", getattr(item, "id", "serialized"))


@pytest.mark.django_db
class TestAbstractManager:
    def test_check_db_return_with_error_dict(self):
        with pytest.raises(ValidationError):
            AbstractManager.check_db_return({"error": "boom"}, DummySerializer)

    def test_check_db_return_queryset(self):
        from django.db.models.query import QuerySet

        item = MagicMock()
        item.value = "one"
        serializer = DummySerializer
        qs = MagicMock(spec=QuerySet)
        qs.__iter__.return_value = iter([item])
        qs.__len__.return_value = 1
        data = AbstractManager.check_db_return(qs, serializer)
        assert data == ["one"]

    def test_check_db_return_single_object(self):
        obj = MagicMock()
        obj.value = "solo"
        data = AbstractManager.check_db_return(obj, DummySerializer)
        assert data == "solo"

    def test_check_body_element_success(self, rf):
        request = types.SimpleNamespace(data={"field": "value"})
        assert AbstractManager.check_body_element(request, "field") == "value"

    def test_check_body_element_missing(self, rf):
        request = types.SimpleNamespace(data={})
        with pytest.raises(ValidationError):
            AbstractManager.check_body_element(request, "field")

    def test_check_query_param_element_str(self, rf):
        request = types.SimpleNamespace(query_params={"flag": "YES"})
        assert AbstractManager.check_query_param_element_str(request, "flag") == "yes"

    def test_check_query_param_element_int(self, rf):
        request = types.SimpleNamespace(query_params={"days": "5"})
        assert AbstractManager.check_query_param_element_int(request, "days") == 5

    def test_check_db_element_exist_success(self):
        team = Teams.objects.create(name="Team")
        found = AbstractManager.check_db_element_exist(Teams, team.id)
        assert found.id == team.id

    def test_check_db_element_exist_missing(self):
        with pytest.raises(ValidationError):
            AbstractManager.check_db_element_exist(Teams, 999)

    def test_check_is_equal_success(self):
        AbstractManager.check_is_equal("alpha", "test", "beta", "test")

    def test_check_is_equal_failure(self):
        with pytest.raises(ValidationError):
            AbstractManager.check_is_equal("alpha", 1, "beta", 2)

    def test_check_is_not_have_element(self):
        obj = types.SimpleNamespace(real_start_time=None)
        AbstractManager.check_is_not_have_element(obj, "real_start_time")

    def test_check_is_not_have_element_raises(self):
        obj = types.SimpleNamespace(real_start_time=datetime.now())
        with pytest.raises(ValidationError):
            AbstractManager.check_is_not_have_element(obj, "real_start_time")

    def test_check_is_have_element(self):
        obj = types.SimpleNamespace(real_start_time=datetime.now())
        AbstractManager.check_is_have_element(obj, "real_start_time")

    def test_check_is_have_element_raises(self):
        obj = types.SimpleNamespace(real_start_time=None)
        with pytest.raises(ValidationError):
            AbstractManager.check_is_have_element(obj, "real_start_time")

    def test_check_if_db_element_with_name_exist_ok(self):
        team = Teams.objects.create(name="Unique")
        with pytest.raises(ValidationError):
            AbstractManager.check_if_db_element_with_name_exist(Teams, "Unique")

    def test_check_if_db_element_with_email_exist(self):
        role, _ = Roles.objects.get_or_create(name="Employee")
        team = Teams.objects.create(name="Alpha")
        Users.objects.create_user(
            email="user@example.com",
            password="pwd",
            first_name="U",
            last_name="S",
            team=team,
            role=role,
        )
        with pytest.raises(ValidationError):
            AbstractManager.check_if_db_element_with_email_exist(Users, "user@example.com")

    def test_check_valid_field_in_kwargs_ok(self):
        AbstractManager.check_valid_field_in_kwargs(Users, email="a@b.c", first_name="foo")

    def test_check_valid_field_in_kwargs_invalid(self):
        with pytest.raises(ValidationError):
            AbstractManager.check_valid_field_in_kwargs(Users, nickname="foo")

    def test_check_valid_shift_interval_success(self, monkeypatch):
        start = datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
        end = start + timedelta(hours=2)
        monkeypatch.setattr(
            "api.service.ShiftRepository.get_shifts_by_user_id",
            lambda user_id: [],
        )
        AbstractManager.check_valid_shift_interval(start, end, user_id=1)

    def test_check_valid_shift_interval_overlap(self, monkeypatch):
        start = datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
        end = start + timedelta(hours=2)
        existing = types.SimpleNamespace(
            start_time=start + timedelta(minutes=30),
            end_time=end + timedelta(hours=1),
        )
        monkeypatch.setattr(
            "api.service.ShiftRepository.get_shifts_by_user_id",
            lambda user_id: [existing],
        )
        with pytest.raises(ValidationError):
            AbstractManager.check_valid_shift_interval(start, end, user_id=1)

    def test_check_is_user_shift_success(self, monkeypatch):
        user = types.SimpleNamespace(id=3)
        shift = types.SimpleNamespace(user=user)
        monkeypatch.setattr("api.service.ShiftRepository.get_shift_by_id", lambda _id: shift)
        AbstractManager.check_is_user_shift(1, 3)

    def test_check_is_user_shift_failure(self, monkeypatch):
        user = types.SimpleNamespace(id=3)
        shift = types.SimpleNamespace(user=user)
        monkeypatch.setattr("api.service.ShiftRepository.get_shift_by_id", lambda _id: shift)
        with pytest.raises(ValidationError):
            AbstractManager.check_is_user_shift(1, 2)
