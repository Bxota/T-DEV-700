import pytest
from unittest.mock import MagicMock, patch

from django.core.exceptions import MultipleObjectsReturned
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

    def test_allows_when_user_is_staff_without_role(self):
        user = MagicMock()
        user.is_authenticated = True
        user.is_staff = True
        delattr(user, "role")
        request = MagicMock(user=user)
        perm = IsTeamManager()
        assert perm.has_permission(request, None) is True

    def test_multiple_objects_returned_fallback(self, monkeypatch):
        user = MagicMock()
        user.is_authenticated = True
        user.role = self.manager_role

        called = {}

        manager_role = self.manager_role

        def fake_filter(**kwargs):
            called["filter"] = True

            class FakeQS:
                def order_by(self, *args, **kwargs):
                    class WithFirst:
                        def first(self_inner):
                            return manager_role

                    return WithFirst()

            return FakeQS()

        monkeypatch.setattr(
            "api.permissions.Roles.objects.get",
            lambda **kwargs: (_ for _ in ()).throw(MultipleObjectsReturned()),
        )
        monkeypatch.setattr("api.permissions.Roles.objects.filter", fake_filter)
        perm = IsTeamManager()
        request = MagicMock(user=user)
        view = MagicMock()
        view.kwargs = {}
        assert perm.has_permission(request, view) is True
        assert called.get("filter")

    def test_has_permission_team_scope_mismatch(self):
        team_a = MagicMock()
        team_a.id = 1
        user = MagicMock()
        user.is_authenticated = True
        user.role = self.manager_role
        user.team_id = 1

        view = MagicMock()
        view.kwargs = {"team_id": 2}

        with patch("api.permissions.Teams.objects.filter", return_value=MagicMock(exists=lambda: True)):
            request = MagicMock(user=user)
            perm = IsTeamManager()
            assert perm.has_permission(request, view) is False

    def test_has_object_permission_requires_matching_team(self):
        team = MagicMock()
        user = MagicMock()
        user.is_authenticated = True
        user.role = self.manager_role
        user.team_id = 5

        obj = MagicMock()
        obj.team_id = 6

        perm = IsTeamManager()
        request = MagicMock(user=user)
        assert perm.has_object_permission(request, MagicMock(), obj) is False

    def test_has_object_permission_allows_when_same_team(self):
        obj = MagicMock()
        obj.team_id = 7
        user = MagicMock()
        user.is_authenticated = True
        user.role = self.manager_role
        user.team_id = 7
        request = MagicMock(user=user)
        perm = IsTeamManager()
        assert perm.has_object_permission(request, MagicMock(), obj) is True
