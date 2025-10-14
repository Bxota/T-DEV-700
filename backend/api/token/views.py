from rest_framework import serializers

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiTypes, inline_serializer

from db_manager.serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer

@extend_schema(
    operation_id="auth_whoami",
    tags=["Auth"],
    summary="Qui suis-je ?",
    description="Retourne les informations de l’utilisateur courant et le payload JWT (si présent).",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def whoami(request):
    return Response({
        "user": {
            "id": request.user.id,
            "first_name": request.user.first_name or "",
            "last_name": request.user.last_name or "",
            "email": request.user.email or "",
            "phone_number": getattr(request.user, "phone_number", None),
            "role": getattr(request.user.role, "name", None),
            "team": getattr(request.user.team, "name", None),
            "is_authenticated": request.user.is_authenticated,
            "is_active": request.user.is_active,
        }
    })

@extend_schema(
    operation_id="token_obtain_pair",
    tags=["Auth"],
    summary="Obtenir un jeton JWT",
    description=(
        "Authentifie un utilisateur (email + mot de passe) et renvoie une paire de jetons : "
        "**access** (court terme) et **refresh** (long terme), avec leurs durées et dates d’expiration."
    ),
    # Requête : ton User a USERNAME_FIELD = 'email'
    request=inline_serializer(
        name="TokenObtainPairRequest",
        fields={
            "email": serializers.EmailField(),
            "password": serializers.CharField(write_only=True),
        },
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="TokenObtainPairResponse",
                fields={
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                    "access_token_expires_at": serializers.DateTimeField(),
                    "refresh_token_expires_at": serializers.DateTimeField(),
                },
            ),
            description="Paire de jetons JWT valide.",
            examples=[
                OpenApiExample(
                    "Exemple de réponse",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                        "access_token_expires_at": "2025-10-14T14:05:12+00:00",
                        "refresh_token_expires_at": "2025-10-21T14:00:12+00:00",
                    },
                )
            ],
        ),
        401: OpenApiResponse(description="Identifiants invalides."),
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT TokenObtainPair avec documentation améliorée"""
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(
    operation_id="token_refresh",
    tags=["Auth"],
    summary="Rafraîchir un jeton JWT",
    description=(
        "Permet d'obtenir un nouveau **access token** à partir d’un **refresh token** valide."
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="TokenObtainPairResponse",
                fields={
                    "access": serializers.CharField(),
                    "access_token_expires_at": serializers.DateTimeField(),
                },
            ),
            description="Paire de jetons JWT valide.",
            examples=[
                OpenApiExample(
                    "Exemple de réponse",
                    value={
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                        "access_token_expires_at": "2025-10-14T14:05:12+00:00",
                    },
                )
            ],
        ),
        401: OpenApiResponse(description="Refresh token expiré ou invalide."),
    },
)
class CustomTokenRefreshView(TokenRefreshView):
    """JWT TokenRefresh avec documentation améliorée"""
    serializer_class = CustomTokenRefreshSerializer