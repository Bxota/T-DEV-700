from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
def health():
    return Response({"message": "Time manager API is healthy."})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def health_authenticated(request):
    user = request.user
    return Response({"message": f"Hello {user.username}, you are authenticated!"})

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
            "username": request.user.username,
            "email": request.user.email,
            "is_authenticated": request.user.is_authenticated,
        },
        "jwt": jwt_payload,
        "method": request.method,
        "path": request.path,
        "query_params": dict(request.query_params),
        "ip": request.META.get("REMOTE_ADDR"),
    })