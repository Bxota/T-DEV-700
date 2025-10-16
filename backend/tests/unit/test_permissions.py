import pytest
from unittest.mock import MagicMock, patch
from api.permissions import IsTeamManager
from db_manager.models import Roles

@pytest.mark.django_db
class TestIsTeamManager:
    def setup_method(self):
        # Crée un rôle manager pour les tests
        self.manager_role = Roles.objects.create(name="manager")

    def test_denies_when_user_not_authenticated(self):
        request = MagicMock()
        request.user = None  # Pas d'utilisateur
        perm = IsTeamManager()
        assert perm.has_permission(request, None) is False

    def test_denies_when_user_not_authenticated_flag(self):
        user = MagicMock()
        user.is_authenticated = False
        request = MagicMock(user=user)
        perm = IsTeamManager()
        assert perm.has_permission(request, None) is False

    def test_allows_when_user_is_manager(self):
        user = MagicMock()
        user.is_authenticated = True
        user.role = self.manager_role  # Rôle identique à celui de la BDD
        request = MagicMock(user=user)
        perm = IsTeamManager()
        assert perm.has_permission(request, None) is True

    def test_denies_when_user_has_other_role(self):
        other_role = Roles.objects.create(name="employee")
        user = MagicMock()
        user.is_authenticated = True
        user.role = other_role
        request = MagicMock(user=user)
        perm = IsTeamManager()
        assert perm.has_permission(request, None) is False

    def test_denies_when_user_has_no_role_attribute(self):
        user = MagicMock()
        user.is_authenticated = True
        delattr(user, "role")  # Simule un utilisateur sans attribut `role`
        request = MagicMock(user=user)
        perm = IsTeamManager()
        assert perm.has_permission(request, None) is False

    def test_handles_exception_from_roles_query(self):
        user = MagicMock()
        user.is_authenticated = True
        user.role = "something"

        request = MagicMock(user=user)
        perm = IsTeamManager()

        with patch("api.permissions.Roles.objects.get", side_effect=Exception("DB down")):
            assert perm.has_permission(request, None) is False
            
    def test_denies_when_manager_role_does_not_exist(self):
        user = MagicMock()
        user.is_authenticated = True
        user.role = "anything"

        request = MagicMock(user=user)
        perm = IsTeamManager()

        # Simule le cas où Roles.objects.get(name='manager') ne trouve rien
        with patch("api.permissions.Roles.objects.get", side_effect=Roles.DoesNotExist):
            assert perm.has_permission(request, None) is False