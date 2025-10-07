from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import HasTeamTagPermission

@api_view(["GET"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def list_users(request):
    return Response([])

@api_view(["GET"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def get_user(request, user_id):
    return Response({"user_id": user_id})

@api_view(["POST"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def add_user(request):
    return Response({"ok": True, "user": request.user.username})

@api_view(["PUT"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def update_user(request, user_id):
    return Response({"updated": True, "user_id": user_id})

@api_view(["DELETE"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def delete_user(request, user_id):
    return Response({"deleted": True, "user_id": user_id})