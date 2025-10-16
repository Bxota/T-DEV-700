from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from api.shifts.service import ShiftManager
from api.shifts.shift_gestion.service import (
    ShiftExceptionManager,
    ShiftRuleManager,
    ShiftTemplateManager,
)

TEST_DATE = datetime.utcnow().date()


@pytest.mark.parametrize(
    "method,input_args,input_kwargs,expected_args,expected_kwargs,repo_path",
    [
        ("list_shifts", tuple(), {}, (), {}, "get_shifts"),
        ("list_shifts_by_user_id", (1,), {}, (), {"user_id": 1}, "get_shifts_by_user_id"),
        ("list_shifts_by_team_id", (2,), {}, (), {"team_id": 2}, "get_shifts_by_team_id"),
        (
            "create_shift",
            ("user", "s", "e"),
            {},
            (),
            {"user": "user", "start_time": "s", "end_time": "e"},
            "create_shift",
        ),
        ("get_shift_by_id", (3,), {}, (3,), {}, "get_shift_by_id"),
        (
            "update_shift",
            (4, "s", "e"),
            {},
            (),
            {"shift_id": 4, "start_time": "s", "end_time": "e"},
            "update_shift",
        ),
        ("delete_shift", (5,), {}, (5,), {}, "delete_shift"),
        ("check_in", (6, "s"), {}, (), {"shift_id": 6, "start_time": "s"}, "check_in"),
        ("check_out", (7, "e"), {}, (), {"shift_id": 7, "end_time": "e"}, "check_out"),
        (
            "list_shifts_by_user_id_and_date",
            (1, "s", "e"),
            {},
            (1, "s", "e"),
            {},
            "list_shifts_by_user_id_and_date",
        ),
    ],
)
def test_shift_manager_methods(method, input_args, input_kwargs, expected_args, expected_kwargs, repo_path, monkeypatch):
    called = {}

    def recorder(*call_args, **call_kwargs):
        called["args"] = call_args
        called["kwargs"] = call_kwargs
        return "ok"

    monkeypatch.setattr(f"api.shifts.service.ShiftRepository.{repo_path}", recorder)
    result = getattr(ShiftManager, method)(*input_args, **input_kwargs)
    assert result == "ok"
    assert called.get("args", ()) == expected_args
    if expected_kwargs:
        for key, value in expected_kwargs.items():
            assert called["kwargs"][key] == value
    else:
        assert called.get("kwargs", {}) == {}


@pytest.mark.parametrize(
    "manager_cls, method, repo_path, input_args, input_kwargs, expected_args, expected_kwargs",
    [
        (
            ShiftTemplateManager,
            "get_shift_template_by_team_id",
            "list_by_team",
            (1,),
            {"active_only": True},
            (1,),
            {"active_only": True},
        ),
        (
            ShiftTemplateManager,
            "get_shift_template_by_id",
            "get_by_id",
            (2,),
            {},
            (2,),
            {},
        ),
        (
            ShiftTemplateManager,
            "create_template",
            "create_template",
            (),
            {"name": "Day", "team_id": 1, "user_id": 2, "default_duration_minutes": 480, "role_id": None},
            (),
            {
                "name": "Day",
                "team_id": 1,
                "created_by_id": 2,
                "default_duration_minutes": 480,
                "timezone": "Europe/Paris",
                "role_id": None,
                "is_active": True,
            },
        ),
        (
            ShiftRuleManager,
            "get_shift_rule_by_template_id",
            "list_by_template",
            (3,),
            {},
            (3,),
            {},
        ),
        (
            ShiftRuleManager,
            "get_shift_rule_by_id",
            "get_by_id",
            (4,),
            {},
            (4,),
            {},
        ),
        (
            ShiftRuleManager,
            "update_rule",
            "update_rule",
            (),
            {"rule_id": 5, "apply_to_whole_team": True},
            (),
            {"rule_id": 5, "apply_to_whole_team": True},
        ),
        (
            ShiftRuleManager,
            "clear_assigned_users",
            "clear_assigned_users",
            (5,),
            {},
            (5,),
            {},
        ),
        (
            ShiftRuleManager,
            "assign_users",
            "assign_users",
            (5, [1, 2]),
            {},
            (5, [1, 2]),
            {},
        ),
        (
            ShiftExceptionManager,
            "get_shift_exception_by_rule_id",
            "list_by_rule",
            (6,),
            {},
            (6,),
            {},
        ),
        (
            ShiftExceptionManager,
            "create_exception",
            "create_exception",
            (),
            {
                "rule_id": 6,
                "date": TEST_DATE,
                "override_start_local_time": None,
                "override_duration_minutes": None,
                "is_skipped": False,
                "note": "",
            },
            (),
            {
                "rule_id": 6,
                "date_value": TEST_DATE,
                "is_skipped": False,
                "override_start_local_time": None,
                "override_duration_minutes": None,
                "note": "",
            },
        ),
    ],
)
def test_shift_gestion_service_wrappers(manager_cls, method, repo_path, input_args, input_kwargs, expected_args, expected_kwargs, monkeypatch):
    called = {}

    def recorder(*call_args, **call_kwargs):
        called["args"] = call_args
        called["kwargs"] = call_kwargs
        return "ok"

    module = "api.shifts.shift_gestion.service"
    monkeypatch.setattr(f"{module}.{manager_cls.__name__.replace('Manager', '')}Repository.{repo_path}", recorder)

    result = getattr(manager_cls, method)(*input_args, **input_kwargs)
    assert result == "ok"

    assert called.get("args", ()) == expected_args
    if expected_kwargs:
        for key, value in expected_kwargs.items():
            assert called["kwargs"][key] == value
    else:
        assert called.get("kwargs", {}) == {}
TEST_DATE = datetime.utcnow().date()
