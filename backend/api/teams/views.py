# api/teams/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from db_manager.models import Teams

from api.teams.service import TeamManager
from api.users.service import UserManager
from api.shifts.service import ShiftManager
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
    members = UserManager.get_users_by_team_id(team_id)
    
    report = []
    for member in members:
        member_shifts = ShiftManager.list_shifts_by_user_id(member.id)
        user_kpis = TeamManager.generate_user_kpi_report(member, member_shifts)
        report.append(user_kpis)
    report.append({"members": members.count()})
    
    return Response(report, status=status.HTTP_200_OK)

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
        try:
            teams = TeamManager.list_teams()

            return Response({"teams": teams}, status=status.HTTP_200_OK)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def post(self, request):
        try:
            name = TeamManager.check_body_element(request, "name")

            TeamManager.check_if_db_element_with_name_exist(Teams, name)

            team = TeamManager.create_team(name)

            team_serialized = TeamManager.check_db_return(team, TeamSerializer)

            return Response({"team": team_serialized}, status=status.HTTP_201_CREATED)

        except APIException as e:
            return Response(e.detail, status=e.status_code)

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
        try:
            team = TeamManager.check_db_element_exist(Teams, id=team_id)

            team = TeamManager.get_team_by_id(team_id)

            team_serialized = TeamManager.check_db_return(team, TeamSerializer)

            return Response({"team": team_serialized}, status=status.HTTP_200_OK)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def put(self, request, team_id):
        try:
            name = TeamManager.check_body_element(request, "name")

            team = TeamManager.check_db_element_exist(Teams, id=team_id)

            new_team = TeamManager.update_team(team_id, name)

            return Response({"is_updated": True, "new_name": new_team.name}, status=status.HTTP_200_OK)

        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def delete(self, request, team_id):
        try:
            team = TeamManager.check_db_element_exist(Teams, id=team_id)

            TeamManager.delete_team(team_id)

            return Response({"is_deleted": True}, status=status.HTTP_200_OK)

        except APIException as e:
            return Response(e.detail, status=e.status_code)