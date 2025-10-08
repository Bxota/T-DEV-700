# api/teams/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from db_manager.repositories.team_repository import TeamRepository

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
def get_team_reports():
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
        responses={201: None},
    ),
)
class TeamCollection(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]  # ex: lecture simple
        if self.request.method == "POST":
            return [IsAuthenticated(), HasTeamTagPermission()]  # ex: création -> tag requis
        return super().get_permissions()

    def get(self, request):
        teams = TeamRepository.get_teams()
        return Response(teams)

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})


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
        team = TeamRepository.get_team_by_id(team_id)
        if team is None:
            return Response({"detail": "Not found."}, status=404)
        return Response({"team_id": team.id, "name": team.name})

    def put(self, request, team_id):
        return Response({"updated": True, "team_id": team_id})

    def delete(self, request, team_id):
        success = TeamRepository.delete_team(team_id)
        if not success:
            return Response({"detail": "Not found."}, status=404)
        return Response(status=204)