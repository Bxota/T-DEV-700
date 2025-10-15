# tests/unit/repositories/test_user_repository.py
import datetime as dt
from unittest.mock import patch, MagicMock
import pytest
from rest_framework.exceptions import APIException

from db_manager.repositories.user_repository import UserRepository

TARGET_USERS = "db_manager.repositories.user_repository.Users"
TARGET_ROLES = "db_manager.repositories.user_repository.Roles"


# ---------------- get_users_by_team_id ----------------
@patch(TARGET_USERS)
def test_get_users_by_team_id_ok(UsersMock):
    filtered = MagicMock()
    expected = MagicMock(name="qs_with_related")
    filtered.select_related.return_value = expected
    UsersMock.objects.filter.return_value = filtered

    res = UserRepository.get_users_by_team_id(team_id=42)
    assert res is expected
    UsersMock.objects.filter.assert_called_once_with(team_id=42)
    filtered.select_related.assert_called_once_with("role", "team")


@patch(TARGET_USERS)
def test_get_users_by_team_id_exception_raises_apiexception(UsersMock):
    UsersMock.objects.filter.side_effect = Exception("db down")

    with pytest.raises(APIException) as err:
        UserRepository.get_users_by_team_id(team_id=42)
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------------- add_user_to_team ----------------
@patch(TARGET_USERS)
def test_add_user_to_team_ok(UsersMock):
    user = MagicMock()
    UsersMock.objects.get.return_value = user

    res = UserRepository.add_user_to_team(user_id=7, team_id=3)
    assert res is user
    assert user.team_id == 3
    user.save.assert_called_once()
    UsersMock.objects.get.assert_called_once_with(id=7)


@patch(TARGET_USERS)
def test_add_user_to_team_exception_raises_apiexception(UsersMock):
    UsersMock.objects.get.side_effect = Exception("boom")
    with pytest.raises(APIException):
        UserRepository.add_user_to_team(user_id=7, team_id=3)


# ---------------- create_user ----------------
@patch(TARGET_USERS)
def test_create_user_ok(UsersMock):
    # L'appel Users(...) renverra une instance configurable
    user_inst = MagicMock()
    # Attributs posés avant save() dans le code -> définissons-les
    user_inst.id = 123
    user_inst.email = "t@ex.com"
    user_inst.first_name = "Tom"
    user_inst.last_name = "Let"
    user_inst.team_id = 5
    user_inst.phone_number = "0600000000"
    user_inst.role_id = 2

    UsersMock.return_value = user_inst  # Users(...) -> user_inst

    res = UserRepository.create_user(
        email="t@ex.com",
        password="secret",
        first_name="Tom",
        last_name="Let",
        team_id=5,
        phone_number="0600000000",
        role_id=2,
    )

    # On vérifie l'appel au setter de mot de passe et au save
    user_inst.set_password.assert_called_once_with("secret")
    user_inst.save.assert_called_once()

    assert res == {
        "id": 123,
        "email": "t@ex.com",
        "first_name": "Tom",
        "last_name": "Let",
        "team_id": 5,
        "phone_number": "0600000000",
        "role_id": 2,
    }


@patch(TARGET_USERS)
def test_create_user_exception_raises_apiexception(UsersMock):
    UsersMock.side_effect = Exception("cannot instantiate")
    with pytest.raises(APIException) as err:
        UserRepository.create_user(email="a@b.c", password="x")
    assert str(err.value.detail["error"]) == "internal server error."
    assert str(err.value.detail["status_code"]) == "500"


# ---------------- get_user_by_id ----------------
@patch(TARGET_USERS)
def test_get_user_by_id_ok(UsersMock):
    user = MagicMock()
    UsersMock.objects.get.return_value = user

    res = UserRepository.get_user_by_id(9)
    assert res is user
    UsersMock.objects.get.assert_called_once_with(id=9)


@patch(TARGET_USERS)
def test_get_user_by_id_not_found_returns_dict(UsersMock):
    # IMPORTANT : DoesNotExist doit être une vraie Exception
    UsersMock.DoesNotExist = type("DoesNotExist", (Exception,), {})
    UsersMock.objects.get.side_effect = UsersMock.DoesNotExist()

    res = UserRepository.get_user_by_id(9)
    assert res == {"error": "User not found"}


@patch("db_manager.repositories.user_repository.Users")
def test_get_user_by_id_generic_exception_returns_error_str(UsersMock):
    UsersMock.DoesNotExist = type("DoesNotExist", (Exception,), {})

    UsersMock.objects.get.side_effect = Exception("db fail")

    from db_manager.repositories.user_repository import UserRepository
    res = UserRepository.get_user_by_id(1)
    assert res == {"error": "db fail"}


# ---------------- update_user ----------------
@patch(TARGET_USERS)
def test_update_user_ok_with_password_and_fields(UsersMock):
    user = MagicMock()
    # Pré-état
    user.id = 1
    user.email = "old@ex.com"
    user.first_name = "Old"
    user.last_name = "Name"
    user.team_id = 2
    user.phone_number = "000"
    user.role_id = 1

    UsersMock.objects.get.return_value = user

    res = UserRepository.update_user(
        1,
        email="new@ex.com",
        first_name="New",
        password="newpass",
        phone_number="0612345678",
    )

    # Le mot de passe passe par set_password
    user.set_password.assert_called_once_with("newpass")
    # Les autres champs via setattr -> on vérifie l'état final attendu
    assert user.email == "new@ex.com"
    assert user.first_name == "New"
    assert user.phone_number == "0612345678"

    user.save.assert_called_once()

    assert res == {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "team_id": user.team_id,
        "phone_number": user.phone_number,
        "role_id": user.role_id,
    }


@patch(TARGET_USERS)
def test_update_user_exception_raises_apiexception(UsersMock):
    UsersMock.objects.get.side_effect = Exception("db err")
    with pytest.raises(APIException):
        UserRepository.update_user(1, email="x@x.x")


# ---------------- get_all_users ----------------
@patch(TARGET_USERS)
def test_get_all_users_ok(UsersMock):
    qs_all = MagicMock()
    expected = MagicMock(name="qs_related")
    qs_all.select_related.return_value = expected
    UsersMock.objects.all.return_value = qs_all

    res = UserRepository.get_all_users()
    assert res is expected
    UsersMock.objects.all.assert_called_once()
    qs_all.select_related.assert_called_once_with("role", "team")


@patch(TARGET_USERS)
def test_get_all_users_exception_raises_apiexception(UsersMock):
    UsersMock.objects.all.side_effect = Exception("down")
    with pytest.raises(APIException):
        UserRepository.get_all_users()


# ---------------- delete_user ----------------
@patch(TARGET_USERS)
def test_delete_user_ok(UsersMock):
    user = MagicMock()
    UsersMock.objects.get.return_value = user

    res = UserRepository.delete_user(4)
    assert res is True
    user.delete.assert_called_once()
    UsersMock.objects.get.assert_called_once_with(id=4)


@patch(TARGET_USERS)
def test_delete_user_exception_raises_apiexception(UsersMock):
    UsersMock.objects.get.side_effect = Exception("nope")
    with pytest.raises(APIException):
        UserRepository.delete_user(4)


# ---------------- delete_user_from_team ----------------
@patch(TARGET_USERS)
def test_delete_user_from_team_ok(UsersMock):
    user = MagicMock()
    UsersMock.objects.get.return_value = user

    res = UserRepository.delete_user_from_team(user_id=10, team_id=2)
    assert res is True
    assert user.team_id is None
    user.save.assert_called_once()
    UsersMock.objects.get.assert_called_once_with(id=10, team_id=2)


@patch(TARGET_USERS)
def test_delete_user_from_team_exception_raises_apiexception(UsersMock):
    UsersMock.objects.get.side_effect = Exception("err")
    with pytest.raises(APIException):
        UserRepository.delete_user_from_team(user_id=10, team_id=2)


# ---------------- get_roles ----------------
@patch(TARGET_ROLES)
def test_get_roles_ok(RolesMock):
    qs = MagicMock()
    RolesMock.objects.all.return_value = qs

    res = UserRepository.get_roles()
    assert res is qs
    RolesMock.objects.all.assert_called_once()


@patch(TARGET_ROLES)
def test_get_roles_exception_raises_apiexception(RolesMock):
    RolesMock.objects.all.side_effect = Exception("boom")
    with pytest.raises(APIException):
        UserRepository.get_roles()