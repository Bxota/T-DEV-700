from django.urls import path

from api.teams.views import list_teams, get_team, add_team, update_team, delete_team

urlpatterns = [
    path("teams/", list_teams, name="list_teams"),              
    path("teams/add/", add_team, name="add_team"),              
    path("teams/<int:team_id>/", get_team, name="get_team"),    
    path("teams/<int:team_id>/update", update_team, name="update_team"), 
    path("teams/<int:team_id>/delete", delete_team, name="delete_team"), 
]