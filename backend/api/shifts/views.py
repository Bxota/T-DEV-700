from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import HasTeamTagPermission

class UserShiftDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PATCH":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})
    
    def delete(self, request):
        return Response({"ok": True, "user": request.user.username})

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

    def get(self, request):
        return Response([])

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})

class TeamShiftCollection(APIView):
    permission_classes = [IsAuthenticated, HasTeamTagPermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        if self.request.method == "PATCH":
            return [IsAuthenticated(), HasTeamTagPermission()]
        if self.request.method == "DELETE":
            return [IsAuthenticated(), HasTeamTagPermission()]
        return [IsAuthenticated()]

    def get(self, request):
        return Response([])

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})