from django.urls import path
from api.teams.views import TeamCollection, TeamDetail, get_team_reports

urlpatterns = [
    path("teams/", TeamCollection.as_view(), name="teams"),
    path("teams/<int:team_id>/", TeamDetail.as_view(), name="team"),
    path("teams/<int:team_id>/reports/", get_team_reports, name="team_reports"),
]