from rest_framework.permissions import BasePermission
from db_manager.models import Roles

class HasTeamTagPermission(BasePermission):
    message = "Vous n'avez pas les permissions nécessaires pour gérer les équipes."

    def has_permission(self, request, view):
        user = request.user
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if not hasattr(user, "role"):
            return False

        try:
            manager_role = Roles.objects.get(name="manager")
        except Roles.DoesNotExist:
            return False
        except Exception:
            return False

        return user.role == manager_role