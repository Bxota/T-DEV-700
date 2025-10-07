from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import HasTeamTagPermission

@api_view(["GET"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def list_teams(request):
    return Response([])

@api_view(["GET"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def get_team(request, team_id):
    return Response({"team_id": team_id})

@api_view(["POST"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def add_team(request):
    return Response({"ok": True, "user": request.user.username})

@api_view(["PUT"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def update_team(request, team_id):
    return Response({"updated": True, "team_id": team_id})

@api_view(["DELETE"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def delete_team(request, team_id):
    return Response({"deleted": True, "team_id": team_id})