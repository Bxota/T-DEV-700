from rest_framework.permissions import BasePermission

class HasTeamTagPermission(BasePermission):
    """
    Permission personnalisée :
    - Requiert que l'utilisateur soit authentifié
    """

    message = "Vous n'avez pas les permissions nécessaires pour gérer les équipes."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if hasattr(user, "role") and user.role == "manager":
            return True

        return False