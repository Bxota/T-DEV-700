from django.urls import path

from api.views.auth import health_authenticated, whoami
from api.views.users import list_users, get_user, add_user, update_user, delete_user
from api.views.teams import list_teams, get_team, add_team, update_team, delete_team
from api.views.shifts import list_shifts, shift_off, shift_on

urlpatterns = [
    # Auth
    path("health/auth/", health_authenticated, name="health_authenticated"),
    path("token/whoami/", whoami, name="whoami"),

    # Users
    path("users/", list_users, name="list_users"),              
    path("users/add/", add_user, name="add_user"),              
    path("users/<int:user_id>/", get_user, name="get_user"),    
    path("users/<int:user_id>/update/", update_user, name="update_user"),  
    path("users/<int:user_id>/delete/", delete_user, name="delete_user"),  

    # Shifts (nested under user)
    path("users/<int:user_id>/shifts/", list_shifts, name="list_user_shifts"),
    path("users/<int:user_id>/shifts/<int:shift_id>/on/", shift_on, name="shift_on"),
    path("users/<int:user_id>/shifts/<int:shift_id>/off/", shift_off, name="shift_off"),

    # Teams
    path("teams/", list_teams, name="list_teams"),              
    path("teams/add/", add_team, name="add_team"),              
    path("teams/<int:team_id>/", get_team, name="get_team"),    
    path("teams/<int:team_id>/update", update_team, name="update_team"), 
    path("teams/<int:team_id>/delete", delete_team, name="delete_team"), 
]