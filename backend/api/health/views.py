from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiTypes
from drf_spectacular.views import SpectacularAPIView

from api.permissions import HasTeamTagPermission

@extend_schema(
    operation_id="health",
    tags=["Health & Schema"],
    summary="Health",
    description="",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
def health(request):
    return Response({"message": "Time manager API is healthy."})

@extend_schema(
    operation_id="health",
    tags=["Health & Schema"],
    summary="Health",
    description="",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def health_authenticated(request):
    user = request.user
    return Response({"message": f"Hello {user.username}, you are authenticated!"})

@extend_schema(
    operation_id="health",
    tags=["Health & Schema"],
    summary="Health",
    description="",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, HasTeamTagPermission])
def health_manager(request):
    user = request.user
    return Response({"message": f"Hello {user.username}, you are a manager!"})

@extend_schema(
    operation_id="schema",
    tags=["Health & Schema"],
    summary="",
    description=(
        ""
    ),
    request={
        "application/json": {
            "refresh": "string"
        }
    },
)
class CustomSchema(SpectacularAPIView):
    """Get Schema ameliore"""
    pass