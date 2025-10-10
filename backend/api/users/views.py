from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.users.service import UserManager

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from api.permissions import HasTeamTagPermission

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
def get_user_reports():
    """
    Rapport possibles : 
    - calculer le taux de retard de l'employé
    - voir son nombre d'absences
    - indiquer le nombre d'heures travaillées
    """
    return Response({})

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
        summary="Lister les utilisateurs d’une équipe",
        description="Retourne la liste des utilisateurs rattachés à l’équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l’équipe"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    ),
    post=extend_schema(
        operation_id="team_user_create",
        tags=["Users"],
        summary="Ajouter un utilisateur à une équipe",
        description="Crée/associe un utilisateur au sein de l’équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l’équipe"),
        ],
        request={"application/json": {"user_id": "int", "team_id": "int"}},
        responses={201: OpenApiTypes.OBJECT},
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
        users = UserManager.get_users_by_team_id(team_id)
        if isinstance(users, dict) and "error" in users:
            return Response(users, status=status.HTTP_404_NOT_FOUND)
        return Response({"users": users})

    def post(self, request, team_id):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not team_id:
            return Response({"error": "team_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        result = UserManager.add_user_to_team(user_id, team_id)
        if isinstance(result, dict) and "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"is_added": True}, status=status.HTTP_201_CREATED)
  
@extend_schema_view(
    get=extend_schema(
        operation_id="user_retrieve",
        tags=["Users"],
        summary="Obtenir un utilisateur",
        description="Retourne les détails d'un utilisateur.",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH, description="Identifiant de l'utilisateur"),
        ],
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
        responses={200: OpenApiTypes.OBJECT},
    ),
    delete=extend_schema(
        operation_id="team_user_delete",
        tags=["Users"],
        summary="Supprimer un utilisateur d’une équipe",
        description="Supprime/dissocie un utilisateur de l’équipe.",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH, description="Identifiant de l’utilisateur"),
        ],
        responses={204: None},
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
        users = UserManager.get_all_users()

        if isinstance(users, dict) and "error" in users:
            return Response(users, status=status.HTTP_400_BAD_REQUEST)

        return Response({"users": users}, status=status.HTTP_200_OK)

    def post(self, request):
        user_data = request.data

        if not user_data.get("email") or not user_data.get("password") or not user_data.get("first_name") or not user_data.get("last_name"):
            return Response({"error": "email, password, first_name and last_name are mandatory."}, status=status.HTTP_400_BAD_REQUEST)

        user = UserManager.create_user(**user_data)

        if isinstance(user, dict) and "error" in user:
            return Response(user, status=status.HTTP_400_BAD_REQUEST)

        return Response({"is_created": True, "user": user}, status=status.HTTP_201_CREATED)

    def put(self, request, team_id):
        return Response({"updated": True, "team_id": team_id})

    def delete(self, request, team_id):
        return Response({"deleted": True, "team_id": team_id})
    
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
        user = UserManager.get_user_by_id(user_id)

        if isinstance(user, dict) and "error" in user:
            return Response(user, status=status.HTTP_400_BAD_REQUEST)

        return Response({"user": user}, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user_data = request.data
        user = UserManager.update_user(user_id, **user_data)

        if isinstance(user, dict) and "error" in user:
            return Response(user, status=status.HTTP_400_BAD_REQUEST)

        return Response({"is_updated": True}, status=status.HTTP_200_OK)
    
    def delete(self, request, user_id):
        result = UserManager.delete_user(user_id)

        if isinstance(result, dict) and "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response({"is_deleted": True}, status=status.HTTP_200_OK)
