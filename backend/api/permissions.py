from rest_framework.permissions import BasePermission

class IsTeamManager(BasePermission):
    message = "Accès réservé aux managers de l'équipe."

    def _is_manager(self, user) -> bool:
        role_name = getattr(getattr(user, "role", None), "name", None)
        return (role_name and role_name.casefold() == "manager") or user.is_staff or user.is_superuser

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", False):
            return False

        team_id = None
        if hasattr(view, "kwargs"):
            team_id = view.kwargs.get("team_id")
        if team_id is None:
            team_id = request.parser_context.get("kwargs", {}).get("team_id") if hasattr(request, "parser_context") else None
        if team_id is None:
            return self._is_manager(user)

        try:
            team_id = int(team_id)
        except (TypeError, ValueError):
            return False

        if getattr(user, "team_id", None) != team_id:
            return False

        return self._is_manager(user)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        obj_team_id = getattr(obj, "team_id", None)
        if obj_team_id is not None and getattr(user, "team_id", None) != obj_team_id:
            return False
        return self._is_manager(user)