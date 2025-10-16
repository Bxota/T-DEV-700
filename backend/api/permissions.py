from django.core.exceptions import MultipleObjectsReturned
from rest_framework.permissions import BasePermission

from db_manager.models import Roles, Teams


class IsTeamManager(BasePermission):
    message = "Accès réservé aux managers de l'équipe."

    def _extract_team_id(self, request, view):
        if getattr(view, "kwargs", None):
            return view.kwargs.get("team_id")
        parser_context = getattr(request, "parser_context", {}) or {}
        return (parser_context.get("kwargs") or {}).get("team_id")

    def _user_has_manager_role(self, user) -> bool:
        if getattr(user, "is_staff", False) is True or getattr(user, "is_superuser", False) is True:
            return True

        team_id = None
        if hasattr(view, "kwargs"):
            team_id = view.kwargs.get("team_id")
        if team_id is None:
            team_id = request.parser_context.get("kwargs", {}).get("team_id") if hasattr(request, "parser_context") else None
        if team_id is None:
            return self._is_manager(user)

        try:
            manager_role = Roles.objects.get(name__iexact="manager")
        except MultipleObjectsReturned:
            manager_role = Roles.objects.filter(name__iexact="manager").order_by("id").first()
        except Roles.DoesNotExist:
            return False
        except Exception:
            return False

        if manager_role is None:
            return False

        user_role = getattr(user, "role", None)
        if isinstance(user_role, Roles):
            if user_role.pk == manager_role.pk:
                return True
            return str(user_role.name).lower() == str(manager_role.name).lower()

        role_name = getattr(user_role, "name", None)
        if role_name and isinstance(role_name, str):
            return role_name.lower() == manager_role.name.lower()

        if isinstance(user_role, str):
            return user_role.lower() == manager_role.name.lower()

        return False

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False

        if not self._user_has_manager_role(user):
            return False

        team_id = self._extract_team_id(request, view)
        if team_id is None:
            return True

        try:
            team_id_int = int(team_id)
        except (TypeError, ValueError):
            return False

        try:
            team_exists = Teams.objects.filter(id=team_id_int).exists()
        except Exception:
            return False

        if team_exists and getattr(user, "team_id", None) != team_id_int:
            return False

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        user = getattr(request, "user", None)
        if not user:
            return False

        if not self._user_has_manager_role(user):
            return False

        obj_team_id = getattr(obj, "team_id", None)
        if obj_team_id is not None and getattr(user, "team_id", None) != obj_team_id:
            return False

        return True
