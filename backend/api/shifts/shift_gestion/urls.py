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
    list_shift_templates_by_team,
    retrieve_shift_template,
    list_shift_rules_by_template,
    retrieve_shift_rule,
    update_shift_template,
    delete_shift_template,
    update_shift_exception,
    delete_shift_exception,
    delete_shift_rule,
    list_shift_exception,
    update_shift_rule,
)

urlpatterns = [
    # Manager / templates & rules
    # Shift Templates
    path(
        "teams/<int:team_id>/shift-templates",
        create_shift_template,
        name="create_shift_template",
    ),
    path(
        "teams/<int:team_id>/shift-templates/list",
        list_shift_templates_by_team,
        name="list_shift_templates_by_team",
    ),
    path(
        "shift-templates/<int:template_id>",
        retrieve_shift_template,
        name="retrieve_shift_template",
    ),
    path(
        "shift-templates/<int:template_id>/update",
        update_shift_template,
        name="update_shift_templates_by_team",
    ),
    path(
        "shift-templates/<int:template_id>/delete",
        delete_shift_template,
        name="delete_shift_templates_by_team",
    ),
    # Shift Rules
    path(
        "shift-rules/<int:rule_id>/update",
        update_shift_rule,
        name="update_shift_rule",
    ),
    path(
        "shift-templates/<int:template_id>/rules", add_shift_rule, name="add_shift_rule"
    ),
    path(
        "shift-templates/<int:template_id>/rules/list",
        list_shift_rules_by_template,
        name="list_shift_rules_by_template",
    ),
    path("shift-rules/<int:rule_id>", retrieve_shift_rule, name="retrieve_shift_rule"),
    path(
        "shift-rules/<int:rule_id>/assign-users",
        assign_rule_users,
        name="assign_rule_users",
    ),
    path(
        "shift-rules/<int:rule_id>/delete", delete_shift_rule, name="delete_shift_rule"
    ),
    # Shift Exceptions
    path(
        "shift-exceptions/list",
        list_shift_exception,
        name="list_shift_exception",
    ),
    path(
        "shift-rules/<int:rule_id>/exceptions",
        add_shift_exception,
        name="add_shift_exception",
    ),
    path(
        "shift-exceptions/<int:exception_id>/update",
        update_shift_exception,
        name="update_shift_exception",
    ),
    path(
        "shift-exceptions/<int:exception_id>/delete",
        delete_shift_exception,
        name="update_shift_exception",
    ),
    # Génération
    path(
        "teams/<int:team_id>/shifts/generate",
        generate_team_shifts,
        name="generate_team_shifts",
    ),
    # Listes Shifts
    path(
        "users/<int:user_id>/shifts/list",
        list_user_shifts_window,
        name="list_user_shifts_window",
    ),
    path("teams/<int:team_id>/calendar", team_calendar_view, name="team_calendar_view"),
]
