# api/teams/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.teams.service import TeamManager
from db_manager.repositories.team_repository import TeamRepository
from db_manager.serializers import TeamSerializer

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter
)

from api.permissions import HasTeamTagPermission

@extend_schema_view(
    get=extend_schema(
        operation_id="team_reports_retrieve",
        tags=["Teams"],
        summary="Récupérer un rapport détaillé sur une équipe",
        description="Retourne le rapport détaillé sur une équipe",
        responses={200: None},
    ),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def get_team_reports(request, team_id):
    """
    Rapport possibles : 
    - calculer le taux de retard de l'équipe
    - voir le nombre d'absences
    - indiquer le nombre d'heures travaillées
    - indiquer le nombre d'employés dans l'équipe
    """
    return Response({})

@extend_schema_view(
    get=extend_schema(
        operation_id="team_list",
        summary="Lister les équipes",
        tags=["Teams"],
        description="Retourne la liste des équipes.",
        responses={200: None},
    ),
    post=extend_schema(
        operation_id="team_create",
        summary="Créer une équipe",
        tags=["Teams"],
        description="Crée une nouvelle équipe et la retourne.",
        request={"application/json": {"name": "string"}},
        responses={201: None},
    ),
)
class TeamCollection(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "POST":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return super().get_permissions()

    def get(self, request):
        teams = TeamManager.list_teams()
        if isinstance(teams, dict) and "error" in teams:
            return Response(teams, status=status.HTTP_400_BAD_REQUEST)
        return Response({"teams": teams})
        teams = TeamRepository.get_teams()
        return Response(teams)

    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response(
                {"error": "Name field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        team = TeamManager.create_team(name)

        if isinstance(team, dict) and "error" in team:
            return Response(team, status=status.HTTP_400_BAD_REQUEST)

        data = TeamSerializer(team).data
        return Response({"team": data}, status=status.HTTP_200_OK)

@extend_schema_view(
    get=extend_schema(
        operation_id="team_retrieve",
        summary="Obtenir une équipe",
        tags=["Teams"],
        description="Détails d'une équipe par identifiant.",
        parameters=[OpenApiParameter("team_id", int, OpenApiParameter.PATH)],
        responses={200: None},
    ),
    put=extend_schema(
        operation_id="team_update",
        summary="Mettre à jour une équipe",
        tags=["Teams"],
        description="Mise à jour partielle d'une équipe.",
        request={"application/json": {"name": "string"}},
        responses={200: None},
    ),
    delete=extend_schema(
        operation_id="team_delete",
        summary="Supprimer une équipe",
        tags=["Teams"],
        description="Supprime définitivement une équipe.",
        responses={204: None},
    ),
)
class TeamDetail(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PUT":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def get(self, request, team_id):
        team = TeamManager.get_team_by_id(team_id)
        if isinstance(team, dict) and "error" in team:
            return Response(team, status=status.HTTP_404_NOT_FOUND)
        return Response({"id": team.id, "name": team.name})
        team = TeamRepository.get_team_by_id(team_id)
        if team is None:
            return Response({"detail": "Not found."}, status=404)
        return Response({"team_id": team.id, "name": team.name})

    def put(self, request, team_id):
        name = request.data.get("name")
        if not name:
            return Response(
                {"error": "Name field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        team = TeamManager.update_team(team_id, name)

        if isinstance(team, dict) and "error" in team:
            return Response(team, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"is_updated": True, "new_name": team.name},
            status=status.HTTP_200_OK
        )

    def delete(self, request, team_id):
        result = TeamManager.delete_team(team_id)

        if isinstance(result, dict) and "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response({"is_deleted": True}, status=status.HTTP_200_OK)
        success = TeamRepository.delete_team(team_id)
        if not success:
            return Response({"detail": "Not found."}, status=404)
        return Response(status=204)
