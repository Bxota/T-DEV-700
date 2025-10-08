from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiTypes

@extend_schema(
    operation_id="auth_whoami",
    tags=["Auth"],
    summary="Qui suis-je ?",
    description="Retourne les informations de l’utilisateur courant et le payload JWT (si présent).",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def whoami(request):
    jwt_payload = None

    if request.auth is not None:
        # SimpleJWT >= 5.x : l'objet AccessToken expose un dict via .payload
        if hasattr(request.auth, "payload"):
            jwt_payload = request.auth.payload
        else:
            try:
                jwt_payload = dict(request.auth)
            except Exception:
                jwt_payload = {"raw": str(request.auth)}

    return Response({
        "user": {
            "id": request.user.id,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "is_authenticated": request.user.is_authenticated,
        },
        "jwt": jwt_payload,
        "method": request.method,
        "path": request.path,
        "query_params": dict(request.query_params),
        "ip": request.META.get("REMOTE_ADDR"),
    })

@extend_schema(
    operation_id="token_obtain_pair",
    tags=["Auth"],
    summary="Obtenir un jeton JWT",
    description=(
        "Authentifie un utilisateur à partir de son nom d’utilisateur et mot de passe.\n\n"
        "Retourne une paire de jetons : **access** (court terme) et **refresh** (long terme)."
    ),
    request={
        "application/json": {
            "username": "string",
            "password": "string"
        }
    },
    responses={
        200: OpenApiResponse(
            description="Paire de jetons JWT valide.",
            examples=[
                OpenApiExample(
                    "Exemple de réponse",
                    value={
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
                    }
                )
            ]
        ),
        401: OpenApiResponse(description="Identifiants invalides."),
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT TokenObtainPair avec documentation améliorée"""
    pass


@extend_schema(
    operation_id="token_refresh",
    tags=["Auth"],
    summary="Rafraîchir un jeton JWT",
    description=(
        "Permet d'obtenir un nouveau **access token** à partir d’un **refresh token** valide."
    ),
    responses={
        200: OpenApiResponse(
            description="Nouveau jeton d'accès valide.",
            examples=[
                OpenApiExample(
                    "Exemple de réponse",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
                    }
                )
            ]
        ),
        401: OpenApiResponse(description="Refresh token expiré ou invalide."),
    },
)
class CustomTokenRefreshView(TokenRefreshView):
    """JWT TokenRefresh avec documentation améliorée"""
    pass