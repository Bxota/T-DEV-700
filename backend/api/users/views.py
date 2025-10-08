from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import HasTeamTagPermission

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