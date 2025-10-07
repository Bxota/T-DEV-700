from django.shortcuts import render


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
def hello(request):
    return Response({"message": "Hello from Django REST API!"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hello_authenticated(request):
    user = request.user
    return Response({"message": f"Hello {user.username}, you are authenticated!"})