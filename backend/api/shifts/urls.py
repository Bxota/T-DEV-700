from django.urls import path

from api.shifts.views import list_user_shifts, shift_user_off, shift_user_on, add_user_shifts, list_team_shifts, add_team_shifts

urlpatterns = [
    path("users/<int:user_id>/shifts/", list_user_shifts, name="list_user_shifts"),
    path("users/<int:user_id>/shifts/add", add_user_shifts, name="add_user_shifts"),
    path("users/<int:user_id>/shifts/<int:shift_id>/on/", shift_user_on, name="shift_on"),
    path("users/<int:user_id>/shifts/<int:shift_id>/off/", shift_user_off, name="shift_off"),
    
    path("teams/<int:team_id>/shifts/", list_team_shifts, name="list_team_shift"),
    path("teams/<int:team_id>/shifts/add", add_team_shifts, name="add_team_shift"),
]
    