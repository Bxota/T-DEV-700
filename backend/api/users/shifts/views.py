from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import HasTeamTagPermission

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_shifts(request):
    return Response([])

@api_view(["POST"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def add_shifts(request):
    return Response([])

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def shift_on(request):
    return Response({})

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def shift_off(request):
    return Response({})