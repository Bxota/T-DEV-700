from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import APIException

from api.shifts.service import ShiftManager
from db_manager.models import Teams, Users, Shifts
from db_manager.serializers import ShiftSerializer


from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
)

from api.permissions import HasTeamTagPermission

@extend_schema(
    operation_id="user_shift_check_in",
    tags=["Shifts - Users"],
    summary="Check in pour le shift sélectionné",
    description="Check in pour le shift sélectionné",
    responses={
        200: ShiftSerializer,
        400: {"error": "..."}
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_shift_check_in(request, user_id, shift_id):
    try:
        start_time = ShiftManager.check_body_element(request, "start_time")
        user: Users = ShiftManager.check_db_element_exist(Users, user_id)
        shift: Shifts = ShiftManager.check_db_element_exist(Shifts, shift_id)
        
        ShiftManager.check_is_equal(shift, shift.user.id, user, user.id)
        ShiftManager.check_is_not_have_element(shift, "real_start_time")
        
        shift = ShiftManager.check_in(shift_id=shift_id, start_time=start_time)

        shift_serialized = ShiftManager.check_db_return(shift, ShiftSerializer)
        return Response({"is_check_in": True, "shift": shift_serialized}, status=status.HTTP_200_OK)
    except APIException as e:
        return Response(e.detail, status=e.status_code)

@extend_schema(
    operation_id="user_shift_check_out",
    tags=["Shifts - Users"],
    summary="Check out pour le shift sélectionné",
    description="Check out pour le shift sélectionné",
    responses={
        200: ShiftSerializer,
        400: {"error": "..."}
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_shift_check_out(request, user_id, shift_id):
    try:
        end_time = ShiftManager.check_body_element(request, 'end_time')
        user: Users = ShiftManager.check_db_element_exist(Users, user_id)
        shift: Shifts = ShiftManager.check_db_element_exist(Shifts, shift_id)
        
        ShiftManager.check_is_equal(shift, shift.user.id, user, user.id)
        ShiftManager.check_is_not_have_element(shift, "real_end_time")
        ShiftManager.check_is_have_element(shift, "real_start_time")
        
        shift = ShiftManager.check_out(shift_id=shift_id, end_time=end_time)
        
        shift_serialized = ShiftManager.check_db_return(shift, ShiftSerializer)
        return Response({"is_check_out": True, "shift": shift_serialized}, status=status.HTTP_200_OK)
        
    except APIException as e:
        return Response(e.detail, status=e.status_code)

@extend_schema_view(
    get=extend_schema(
        operation_id="user_shift_retrieve",
        tags=["Shifts - Users"],
        summary="Obtenir un shift d'un utilisateur",
        parameters=[
            OpenApiParameter("user_id", int, OpenApiParameter.PATH),
            OpenApiParameter("shift_id", int, OpenApiParameter.PATH),
        ],
        responses={
            200: ShiftSerializer,
            400: {"error": "..."}
        }
    ),
    put=extend_schema(
        operation_id="user_shift_update",
        tags=["Shifts - Users"],
        summary="Mettre à jour un shift d'un utilisateur",
    ),
    delete=extend_schema(
        operation_id="user_shift_delete",
        tags=["Shifts - Users"],
        summary="Supprimer un shift d'un utilisateur",
    ),
)
class UserShiftDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PUT":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]
    
    def get(self, request, user_id, shift_id):
        try:
            ShiftManager.check_db_element_exist(Users, user_id)
            ShiftManager.check_db_element_exist(Shifts, shift_id)

            ShiftManager.check_is_user_shift(shift_id, user_id)

            shift = ShiftManager.get_shift_by_id(shift_id=shift_id)

            shift_serialized = ShiftSerializer(shift).data
            return Response({"shift": shift_serialized}, status=status.HTTP_200_OK)
        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def put(self, request, user_id, shift_id):
        try:
            ShiftManager.check_db_element_exist(Users, user_id)
            ShiftManager.check_db_element_exist(Shifts, shift_id)

            ShiftManager.check_is_user_shift(shift_id, user_id)

            ShiftManager.check_body_element(request, "start_time")
            ShiftManager.check_body_element(request, "end_time")

            ShiftManager.check_valid_shift_interval(
                start_time=datetime.fromisoformat(request.data.get("start_time").replace("Z", "+00:00")),
                end_time=datetime.fromisoformat(request.data.get("end_time").replace("Z", "+00:00")),
                user_id=user_id
            )

            ShiftManager.update_shift(
                shift_id=shift_id,
                start_time=request.data.get("start_time"),
                end_time=request.data.get("end_time")
            )
            
            return Response({"is_updated": True}, status=status.HTTP_200_OK)
        except APIException as e:
            return Response(e.detail, status=e.status_code)
    
    def delete(self, request, user_id, shift_id):
        try:
            ShiftManager.check_db_element_exist(Users, user_id)
            ShiftManager.check_db_element_exist(Shifts, shift_id)

            ShiftManager.check_is_user_shift(shift_id, user_id)

            ShiftManager.delete_shift(shift_id=shift_id)

            return Response({"is_deleted": True}, status=status.HTTP_200_OK)
        except APIException as e:
            return Response(e.detail, status=e.status_code)

@extend_schema_view(
    get=extend_schema(
        operation_id="user_shift_list",
        summary="Lister les shifts d’un utilisateur",
        tags=["Shifts - Users"],
        parameters=[OpenApiParameter("user_id", int, OpenApiParameter.PATH)],
    ),
    post=extend_schema(
        operation_id="user_shift_create",
        summary="Créer un shift pour un utilisateur",
        tags=["Shifts - Users"],
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

    def get(self, request, user_id):
        try:
            ShiftManager.check_db_element_exist(Users, user_id)

            shifts = ShiftManager.list_shifts_by_user_id(user_id)
            shifts_serialized = ShiftManager.check_db_return(shifts, ShiftSerializer)

            return Response({"shifts": shifts_serialized}, status=status.HTTP_200_OK)

        except APIException as e:
            return Response(e.detail, status=e.status_code)

    def post(self, request, user_id):
        try:
            ShiftManager.check_db_element_exist(Users, user_id)

            ShiftManager.check_body_element(request, "start_time")
            ShiftManager.check_body_element(request, "end_time")

            ShiftManager.check_valid_shift_interval(
                start_time=datetime.fromisoformat(request.data.get("start_time").replace("Z", "+00:00")),
                end_time=datetime.fromisoformat(request.data.get("end_time").replace("Z", "+00:00")),
                user_id=user_id
            )

            shift = ShiftManager.create_shift(
                user=Users.objects.get(pk=user_id),
                start_time=request.data.get("start_time"),
                end_time=request.data.get("end_time")
            )

            return Response({"is_created": True, "id": shift.id}, status=status.HTTP_201_CREATED)
        
        except APIException as e:
            return Response(e.detail, status=e.status_code)

@extend_schema_view(
    get=extend_schema(
        operation_id="team_shift_list",
        tags=["Shifts - Teams"],
        summary="Lister les shifts (équipe)",
        description="Retourne la liste des shifts (portée équipe).",
        responses={200: OpenApiTypes.OBJECT},
    ),
)
class TeamShiftCollection(APIView):
    permission_classes = [IsAuthenticated, HasTeamTagPermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), HasTeamTagPermission()]

    def get(self, request, team_id):
        try:
            ShiftManager.check_db_element_exist(Teams, team_id)

            shifts = ShiftManager.list_shifts_by_team_id(team_id)
            shifts_serialized = ShiftManager.check_db_return(shifts, ShiftSerializer)

            return Response({"shifts": shifts_serialized}, status=status.HTTP_200_OK)

        except APIException as e:
            return Response(e.detail, status=e.status_code)
        
