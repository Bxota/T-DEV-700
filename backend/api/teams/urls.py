from django.urls import path
from api.teams.views import TeamCollection, TeamDetail

urlpatterns = [
    path("teams/", TeamCollection.as_view(), name="teams"),
    path("teams/<int:team_id>/", TeamDetail.as_view(), name="team"),
]