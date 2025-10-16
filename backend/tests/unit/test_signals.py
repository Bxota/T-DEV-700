import importlib

import pytest

from db_manager.models import Roles


@pytest.mark.django_db
def test_create_default_roles_signal():
    Roles.objects.all().delete()
    module = importlib.import_module("db_manager.signals")
    module.create_default_roles(sender=None)
    assert set(Roles.objects.values_list("name", flat=True)) == {"Manager", "Employee"}
