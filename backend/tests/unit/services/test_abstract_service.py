import json
import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from api.service import AbstractManager
from unittest.mock import MagicMock


# --------------------------
# check_db_return
# --------------------------

def test_check_db_return_with_error():
    with pytest.raises(ValidationError) as exc:
        AbstractManager.check_db_return({"error": "Something went wrong"}, MagicMock())
    assert exc.value.detail == {"error": "Something went wrong"}


def test_check_db_return_with_valid_object():
    mock_obj = MagicMock()
    mock_serializer = MagicMock()
    mock_serializer.return_value.data = {"id": 1}

    result = AbstractManager.check_db_return(mock_obj, mock_serializer)

    mock_serializer.assert_called_once_with(mock_obj)
    assert result == {"id": 1}

# --------------------------
# check_db_element_exist
# --------------------------

class DummyModel:
    class DoesNotExist(Exception):
        pass

    objects = MagicMock()

def test_check_db_element_exist_found():
    dummy_instance = MagicMock()
    DummyModel.objects.get.return_value = dummy_instance

    result = AbstractManager.check_db_element_exist(DummyModel, 123)
    assert result == dummy_instance
    DummyModel.objects.get.assert_called_once_with(pk=123)

def test_check_db_element_exist_not_found():
    DummyModel.objects.get.side_effect = DummyModel.DoesNotExist()

    with pytest.raises(ValidationError) as exc:
        AbstractManager.check_db_element_exist(DummyModel, 123)

    assert exc.value.detail == {"error": "dummymodel not found."}


# --------------------------
# check_is_equal
# --------------------------

def test_check_is_equal_ok():
    AbstractManager.check_is_equal("x", 1, "y", 1)  # no exception

def test_check_is_equal_fail():
    with pytest.raises(ValidationError) as exc:
        AbstractManager.check_is_equal("x", 1, "y", 2)
    assert "are not linked" in str(exc.value.detail["error"])


# --------------------------
# check_is_not_have_element
# --------------------------

class DummyObj:
    def __init__(self, attr=None):
        self.attr = attr

def test_check_is_not_have_element_ok():
    obj = DummyObj(attr=None)
    AbstractManager.check_is_not_have_element(obj, "attr")  # should pass

def test_check_is_not_have_element_fail():
    obj = DummyObj(attr="value")
    with pytest.raises(ValidationError) as exc:
        AbstractManager.check_is_not_have_element(obj, "attr")
    assert "already has a attr element" in str(exc.value.detail["error"])


# --------------------------
# check_is_have_element
# --------------------------

def test_check_is_have_element_ok():
    obj = DummyObj(attr="value")
    AbstractManager.check_is_have_element(obj, "attr")  # should pass

def test_check_is_have_element_fail():
    obj = DummyObj(attr=None)
    with pytest.raises(ValidationError) as exc:
        AbstractManager.check_is_have_element(obj, "attr")
    assert "doesn't has a attr element" in str(exc.value.detail["error"])