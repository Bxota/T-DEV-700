from db_manager.models import Teams, Users
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.users.service import UserManager
from rest_framework.exceptions import APIException

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from api.permissions import HasTeamTagPermission
from api.teams.service import TeamManager
from api.shifts.service import ShiftManager
from db_manager.serializers import UserSerializer

@extend_schema_view(
    get=extend_schema(
        operation_id="user_reports",
        tags=["Users"],
        summary="Récupérer un rapport détaillé sur un employé",
        description="Retourne le rapport détaillé sur un employé",
        responses={200: None},
    ),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_reports(request, user_id):
    user = UserManager.get_user_by_id(user_id)
    
    user_shifts = ShiftManager.list_shifts_by_user_id(user.id)
    user_kpis = TeamManager.generate_user_kpi_report(user, user_shifts)
    
    return Response(user_kpis, status=status.HTTP_200_OK)

@extend_schema_view(
    get=extend_schema(
        operation_id="user_clocks",
        tags=["Users"],
        summary="Get a summary of the arrivals and departures of an employee",
        description="Get a summary of the arrivals and departures of an employee",
        responses={200: None},
    ),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_clocks_summary():
    """
    Renvoie les heures de départs et d'arrivées de l'employé
    """
    return Response({})

@extend_schema_view(
    get=extend_schema(
        operation_id="team_user_list",
        tags=["Users"],
        summary="Lister les utilisateurs d'une équipe",
        description="Retourne la liste des utilisateurs rattachés à l'équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l'équipe"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    ),
    post=extend_schema(
        operation_id="team_user_create",
        tags=["Users"],
        summary="Ajouter un utilisateur à une équipe",
        description="Crée/associe un utilisateur au sein de l'équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l'équipe"),
        ],
        request={"application/json": {"user_id": "int", "team_id": "int"}},
        responses={201: OpenApiTypes.OBJECT},
    ),
    delete=extend_schema(
        operation_id="team_user_delete",
        tags=["Users"],
        summary="Supprimer un utilisateur d'une équipe",
        description="Supprime/dissocie un utilisateur de l'équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l'équipe"),
        ],
        request={"application/json": {"user_id": "int", "team_id": "int"}},
        responses={200: OpenApiTypes.OBJECT},
    ),
)
class UserTeamCollection(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "POST":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]
    
    def get(self, request, team_id):
        try:
            UserManager.check_db_element_exist(Teams, team_id)

            users = UserManager.get_users_by_team_id(team_id)
            
            users_serialized = UserManager.check_db_return(users, UserSerializer)

            return Response({"users": users_serialized}, status=status.HTTP_200_OK)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def post(self, request, team_id):
        try:
            UserManager.check_db_element_exist(Teams, team_id)

            UserManager.check_body_element(request, "user_id")

            UserManager.check_db_element_exist(Users, request.data.get("user_id"))

            UserManager.add_user_to_team(request.data.get("user_id"), team_id)

            return Response({"is_added": True}, status=status.HTTP_201_CREATED)

        except APIException as e:
            return Response(e.detail, status=e.status_code)
    
    def delete(self, request, team_id):
        try:
            UserManager.check_db_element_exist(Teams, team_id)

            UserManager.check_body_element(request, "user_id")

            UserManager.check_db_element_exist(Users, request.data.get("user_id"))

            UserManager.delete_user_from_team(request.data.get("user_id"), team_id)

            return Response({"is_deleted": True}, status=status.HTTP_200_OK)
        except APIException as e:
            return Response(e.detail, status=e.status_code)

@extend_schema_view(
    get=extend_schema(
        operation_id="user_retrieve",
        tags=["Users"],
        summary="Retourne tous les utilisateurs",
        description="Retourne tous les utilisateurs",
        parameters=[],
        responses={200: OpenApiTypes.OBJECT},
    ),
    post=extend_schema(
        operation_id="user_create",
        tags=["Users"],
        summary="Ajouter un utilisateur",
        description="Crée un utilisateur.",
        request={"application/json": { "email": "str", "password": "str", "first_name": "str", "last_name": "str", "team_id": "int", "phone_number": "str", "role_id": "int"}},
        responses={201: OpenApiTypes.OBJECT},
    ),
    put=extend_schema(
        operation_id="team_user_update",
        tags=["Users"],
        summary="Mettre à jour un utilisateur d'une équipe",
        description="Met à jour un utilisateur rattaché à l'équipe.",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH, description="Identifiant de l'utilisateur"),
        ],
        request={"application/json": {"last_name": "string", "first_name": "string", "email": "string", "phone_number": "string", "role_id": "int", "password": "string", "team_id": "int"}},   
        responses={200: OpenApiTypes.OBJECT},
    ),
)
class UserCollection(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "POST":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "PUT":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def get(self, request):
        try:
            users = UserManager.get_all_users()

            users_serialized = UserManager.check_db_return(users, UserSerializer)

            return Response({"users": users_serialized}, status=status.HTTP_200_OK)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def post(self, request):
        try:
            user_data = request.data

            UserManager.check_body_element(request, "email")
            UserManager.check_body_element(request, "password")

            UserManager.check_if_db_element_with_email_exist(Users, request.data.get("email"))

            user = UserManager.create_user(**user_data)

            return Response({"user": user}, status=status.HTTP_201_CREATED)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)
    
@extend_schema_view(
    get=extend_schema(
        operation_id="user_detail",
        tags=["Users"],
        summary="detail d'un utilisateur",
        description="Retourne les détails d'un utilisateur.",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH, description="Identifiant de l'utilisateur"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    ),
    put=extend_schema(
        operation_id="user_update",
        tags=["Users"],
        summary="Modifier un utilisateur",
        description="Met à jour un utilisateur.",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH, description="Identifiant de l'utilisateur"),
        ],
        request={"application/json": {"last_name": "string", "first_name": "string", "email": "string", "phone_number": "string", "role_id": "int", "password": "string", "team_id": "int"}},
        responses={201: OpenApiTypes.OBJECT},
    ),
    delete=extend_schema(
        operation_id="user_delete",
        tags=["Users"],
        summary="Supprimer un utilisateur",
        description="Supprime définitivement un utilisateur.",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH, description="Identifiant de l'utilisateur"),
        ],
        responses={204: None},
    ),
)
class UserDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PUT":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]
    
    def get(self, request, user_id):
        try:
            user = UserManager.get_user_by_id(user_id)
            
            user_serialized = UserManager.check_db_return(user, UserSerializer)

            return Response({"user": user_serialized}, status=status.HTTP_200_OK)
        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def put(self, request, user_id):
        try:
            UserManager.check_db_element_exist(Users, user_id)
            
            UserManager.check_valid_field_in_kwargs(Users, **request.data)
            
            UserManager.update_user(user_id, **request.data)

            return Response({"is_updated": True}, status=status.HTTP_200_OK)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)
    
    def delete(self, request, user_id):
        try:
            UserManager.check_db_element_exist(Users, user_id)

            UserManager.delete_user(user_id)

            return Response({"is_deleted": True}, status=status.HTTP_200_OK)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)
