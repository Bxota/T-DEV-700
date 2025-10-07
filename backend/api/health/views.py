from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import HasTeamTagPermission

@api_view(["GET"])
def health():
    return Response({"message": "Time manager API is healthy."})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def health_authenticated(request):
    user = request.user
    return Response({"message": f"Hello {user.username}, you are authenticated!"})

@api_view(["GET"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def health_manager(request):
    user = request.user
    return Response({"message": f"Hello {user.username}, you are a manager!"})