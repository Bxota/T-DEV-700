from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from api.permissions import HasTeamTagPermission

@extend_schema_view(
    get=extend_schema(
        operation_id="user_shift_retrieve",
        tags=["Shifts"],
        summary="Obtenir un shift d’un utilisateur",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH),
            OpenApiParameter("shift_id", int, OpenApiParameter.PATH),
        ],
    ),
    post=extend_schema(
        operation_id="user_shift_update",
        tags=["Shifts"],
        summary="Mettre à jour un shift d’un utilisateur",
    ),
    delete=extend_schema(
        operation_id="user_shift_delete",
        tags=["Shifts"],
        summary="Supprimer un shift d’un utilisateur",
    ),
)
class UserShiftDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PATCH":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})
    
    def delete(self, request):
        return Response({"ok": True, "user": request.user.username})

@extend_schema_view(
    get=extend_schema(
        operation_id="user_shift_list",
        summary="Lister les shifts d’un utilisateur",
        tags=["Shifts"],
        parameters=[OpenApiParameter("user_id", int, OpenApiParameter.PATH)],
    ),
    post=extend_schema(
        operation_id="user_shift_create",
        summary="Créer un shift pour un utilisateur",
        tags=["Shifts"],
        parameters=[OpenApiParameter("user_id", int, OpenApiParameter.PATH)],
    ),
)
class UserShiftCollection(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PATCH":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def get(self, request):
        return Response([])

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})

@extend_schema_view(
    get=extend_schema(
        operation_id="team_shift_list",
        tags=["Shifts"],
        summary="Lister les shifts (équipe)",
        description="Retourne la liste des shifts (portée équipe).",
        responses={200: OpenApiTypes.OBJECT},
    ),
    post=extend_schema(
        operation_id="team_shift_create",
        tags=["Shifts"],
        summary="Créer un shift (équipe)",
        description="Crée un nouveau shift au niveau de l’équipe.",
        responses={201: OpenApiTypes.OBJECT},
    ),
)
class TeamShiftCollection(APIView):
    permission_classes = [IsAuthenticated, HasTeamTagPermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PATCH":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def get(self, request):
        return Response([])

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})