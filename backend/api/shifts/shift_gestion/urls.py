# api/shifts/urls_manager.py
from django.urls import path
from api.shifts.shift_gestion.views import (
    create_shift_template,
    add_shift_rule,
    assign_rule_users,
    add_shift_exception,
    generate_team_shifts,
    list_user_shifts_window,
    team_calendar_view,
)

urlpatterns = [
    # Manager / templates & rules
    path("teams/<int:team_id>/shift-templates", create_shift_template, name="create_shift_template"),
    path("shift-templates/<int:template_id>/rules", add_shift_rule, name="add_shift_rule"),
    path("shift-rules/<int:rule_id>/assign-users", assign_rule_users, name="assign_rule_users"),
    path("shift-rules/<int:rule_id>/exceptions", add_shift_exception, name="add_shift_exception"),

    # Génération
    path("teams/<int:team_id>/shifts/generate", generate_team_shifts, name="generate_team_shifts"),

    # Listes
    path("users/<int:user_id>/shifts", list_user_shifts_window, name="list_user_shifts_window"),
    path("teams/<int:team_id>/calendar", team_calendar_view, name="team_calendar_view"),
]