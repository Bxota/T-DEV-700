# api/teams/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.permissions import HasTeamTagPermission

class TeamCollection(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]  # ex: lecture simple
        if self.request.method == "POST":
            return [IsAuthenticated(), HasTeamTagPermission()]  # ex: création -> tag requis
        return super().get_permissions()

    def get(self, request):
        return Response([])

    def post(self, request):
        return Response({"ok": True, "user": request.user.username})


class TeamDetail(APIView):
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