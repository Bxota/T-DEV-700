from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from api.permissions import HasTeamTagPermission

@extend_schema_view(
    get=extend_schema(
        operation_id="user_reports_retrieve",
        tags=["Reports"],
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
        responses={201: OpenApiTypes.OBJECT},
    ),
)
class UserCollection(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "POST":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]
    
    def get(self, request, team_id):
        return Response({"team_id": team_id})

    def post(self, request, team_id):
        return Response({"updated": True, "team_id": team_id})
  
@extend_schema_view(
    get=extend_schema(
        operation_id="team_user_retrieve",
        tags=["Users"],
        summary="Obtenir un utilisateur d’une équipe",
        description="Retourne les détails d’un utilisateur rattaché à l’équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l’équipe"),
            # NOTE: Si tu ajoutes user_id dans l’URL plus tard, rajoute-le ici
        ],
        responses={200: OpenApiTypes.OBJECT},
    ),
    put=extend_schema(
        operation_id="team_user_update",
        tags=["Users"],
        summary="Mettre à jour un utilisateur d’une équipe",
        description="Met à jour un utilisateur rattaché à l’équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l’équipe"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    ),
    delete=extend_schema(
        operation_id="team_user_delete",
        tags=["Users"],
        summary="Supprimer un utilisateur d’une équipe",
        description="Supprime/dissocie un utilisateur de l’équipe.",
        parameters=[
            OpenApiParameter("team_id", int, OpenApiParameter.PATH, description="Identifiant de l’équipe"),
        ],
        responses={204: None},
    ),
)  
class UserDetail(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PUT":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def get(self, request, team_id):
        return Response({"team_id": team_id})

    def put(self, request, team_id):
        return Response({"updated": True, "team_id": team_id})

    def delete(self, request, team_id):
        return Response({"deleted": True, "team_id": team_id})