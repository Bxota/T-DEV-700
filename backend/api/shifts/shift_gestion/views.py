# api/shifts/views_manager.py
from datetime import date, timedelta
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status

from api.permissions import IsTeamManager
from api.shifts.service import ShiftManager
from api.users.service import UserManager
from api.shifts.shift_gestion.service import (
    ShiftExceptionManager,
    ShiftRuleManager,
    ShiftTemplateManager,
)

from db_manager.models import Users, Shifts
from db_manager.repositories.shift_template_repository import ShiftTemplateRepository
from db_manager.repositories.shift_rule_repository import ShiftRuleRepository
from db_manager.serializers import (
    ShiftTemplateSerializer,
    ShiftRuleSerializer,
    ShiftExceptionSerializer,
    ShiftSerializer,
)

from api.shifts.shift_gestion.serializer import (
    CreateTemplateInput,
    UpdateTemplateInput,
    CreateRuleInput,
    AssignUsersInput,
    CreateExceptionInput,
    UpdateExceptionInput,
)
from api.shifts.generator import generate_occurrences_for_window

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

# --- 1) POST /api/teams/{team_id}/shift-templates/ ---


@extend_schema(
    operation_id="shift_template_create",
    tags=["Shifts · Manager · Template"],
    summary="Créer un modèle de shift (manager)",
    description="Crée un **ShiftTemplate** pour l'équipe donnée. Accès réservé aux managers de l'équipe.",
    request=CreateTemplateInput,
    responses={
        201: OpenApiResponse(
            description="Modèle créé",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "id": 12,
                        "name": "Matin standard",
                        "team_id": 4,
                        "role_id": None,
                        "default_duration_minutes": 480,
                        "timezone": "Europe/Paris",
                        "is_active": True,
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / Conflit"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
    },
    parameters=[
        OpenApiParameter(
            name="team_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeamManager])
def create_shift_template(request, team_id: int):
    try:
        serializer = CreateTemplateInput(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = serializer.validated_data
        res = ShiftTemplateManager.create_template(
            name=payload["name"],
            team_id=team_id,
            user_id=request.user.id,
            default_duration_minutes=payload["default_duration_minutes"],
            timezone=payload.get("timezone", "Europe/Paris"),
            role_id=payload.get("role_id"),
            is_active=payload.get("is_active", True),
        )

        res_serialized = ShiftTemplateManager.check_db_return(
            res, ShiftTemplateSerializer
        )

        return Response(res_serialized, status=status.HTTP_201_CREATED)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- LIST & RETRIEVE: Shift Templates (manager only) ---
@extend_schema(
    operation_id="shift_template_list_by_team",
    tags=["Shifts · Manager · Template"],
    summary="Lister les ShiftTemplates d'une équipe (manager)",
    description="Retourne les modèles de shift pour l’équipe donnée. Accès réservé aux managers de l’équipe.",
    responses={
        200: OpenApiResponse(
            description="Liste des templates",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "count": 1,
                        "results": [
                            {
                                "id": 12,
                                "name": "Matin standard",
                                "team_id": 4,
                                "role_id": None,
                                "default_duration_minutes": 480,
                                "timezone": "Europe/Paris",
                                "is_active": True,
                            }
                        ],
                    },
                )
            ],
        ),
        403: OpenApiResponse(description="Interdit (manager requis)"),
    },
    parameters=[
        OpenApiParameter(
            name="team_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
        OpenApiParameter(
            name="active_only",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filtrer uniquement les templates actifs (true/false).",
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeamManager])
def list_shift_templates_by_team(request, team_id: int):
    try:
        active_only = ShiftTemplateManager.check_query_param_element_str(
            request, "active_only"
        ) in ("1", "true", "yes")
        qs = ShiftTemplateManager.get_shift_template_by_team_id(
            team_id, active_only
        ).order_by("name", "id")

        qs_serialized = ShiftTemplateManager.check_db_return(
            qs, ShiftTemplateSerializer
        )

        return Response(
            {"count": len(qs), "results": qs_serialized}, status=status.HTTP_200_OK
        )
    except APIException as e:
        return Response(e.detail, status=e.status_code)


@extend_schema(
    operation_id="shift_template_update",
    tags=["Shifts · Manager · Template"],
    summary="Mise à jour d'un ShiftTemplate (manager)",
    description="Modifie le Template.",
    request=UpdateTemplateInput,
    responses={
        200: OpenApiResponse(
            description="Détail du template",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "id": 12,
                        "name": "Matin standard",
                        "team_id": 4,
                        "role_id": None,
                        "default_duration_minutes": 480,
                        "timezone": "Europe/Paris",
                        "is_active": True,
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftTemplate introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="template_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeamManager])
def update_shift_template(request, template_id: int):
    try:
        serializer = UpdateTemplateInput(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = serializer.validated_data
        res = ShiftTemplateManager.update_template(
            template_id=template_id,
            name=payload["name"],
            default_duration_minutes=payload["default_duration_minutes"],
            timezone=payload.get("timezone", "Europe/Paris"),
            role_id=payload.get("role_id"),
            is_active=payload.get("is_active", True),
        )

        res_serialized = ShiftTemplateManager.check_db_return(
            res, ShiftTemplateSerializer
        )

        return Response(res_serialized, status=status.HTTP_200_OK)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


@extend_schema(
    operation_id="shift_template_delete",
    tags=["Shifts · Manager · Template"],
    summary="Supprimer un ShiftTemplate (manager)",
    description="Supprime définitivement le Template.",
    responses={
        204: OpenApiResponse(description="Template supprimé"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftTemplate introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="template_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeamManager])
def delete_shift_template(request, template_id: int):
    try:
        res = ShiftTemplateManager.delete_template(template_id=template_id)
        if isinstance(res, dict) and "error" in res:
            return Response(res, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


@extend_schema(
    operation_id="shift_template_retrieve",
    tags=["Shifts · Manager · Template"],
    summary="Détail d'un ShiftTemplate (manager)",
    description="Retourne le template, ses règles et leurs exceptions.",
    responses={
        200: OpenApiResponse(
            description="Détail du template",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "id": 12,
                        "name": "Matin standard",
                        "team_id": 4,
                        "role_id": None,
                        "default_duration_minutes": 480,
                        "timezone": "Europe/Paris",
                        "is_active": True,
                        "rules": [
                            {
                                "id": 31,
                                "weekday": 2,
                                "start_local_time": "08:00:00",
                                "duration_minutes": 480,
                                "effective_from": "2025-10-01",
                                "effective_to": None,
                                "apply_to_whole_team": True,
                                "assigned_user_ids": [],
                                "exceptions": [
                                    {
                                        "id": 7,
                                        "date": "2025-10-15",
                                        "is_skipped": True,
                                        "override_start_local_time": None,
                                        "override_duration_minutes": None,
                                        "note": "Férié local",
                                    }
                                ],
                            }
                        ],
                    },
                )
            ],
        ),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftTemplate introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="template_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeamManager])
def retrieve_shift_template(request, template_id: int):
    try:
        tpl = ShiftTemplateManager.get_shift_template_by_id(template_id)
        rules_qs = ShiftRuleManager.get_shift_rule_by_template_id(tpl.id).order_by(
            "weekday", "start_local_time"
        )

        tpl_serialized = ShiftTemplateManager.check_db_return(
            tpl, ShiftTemplateSerializer
        )
        rules_serialized = []

        for r in rules_qs:
            r_serialized = ShiftRuleManager.check_db_return(r, ShiftRuleSerializer)

            # Récupérer les exceptions triées pour CETTE règle
            ex_qs = ShiftExceptionManager.get_shift_exception_by_rule_id(
                rule_id=r.id
            ).order_by("date")
            ex_serialized = ShiftExceptionManager.check_db_return(
                ex_qs, ShiftExceptionSerializer
            )

            # Attacher au dict de la règle
            r_serialized["exceptions"] = ex_serialized
            rules_serialized.append(r_serialized)

        tpl_serialized["rules"] = rules_serialized

        return Response(tpl_serialized, status=status.HTTP_200_OK)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- GET /api/shift-templates/{template_id}/rules ---
@extend_schema(
    operation_id="shift_rule_list_by_template",
    tags=["Shifts · Manager · Rule"],
    summary="Lister les ShiftRules d'un template (manager)",
    description="Retourne la liste des règles récurrentes associées à un ShiftTemplate donné.",
    responses={
        200: OpenApiResponse(
            description="Liste des règles",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "count": 2,
                        "results": [
                            {
                                "id": 31,
                                "weekday": 2,
                                "start_local_time": "08:00:00",
                                "duration_minutes": 480,
                                "effective_from": "2025-10-01",
                                "effective_to": None,
                                "apply_to_whole_team": True,
                                "assigned_user_ids": [],
                            },
                            {
                                "id": 32,
                                "weekday": 4,
                                "start_local_time": "09:00:00",
                                "duration_minutes": 420,
                                "effective_from": "2025-10-01",
                                "effective_to": "2026-01-01",
                                "apply_to_whole_team": False,
                                "assigned_user_ids": [8, 9],
                            },
                        ],
                    },
                )
            ],
        ),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftTemplate introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="template_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeamManager])
def list_shift_rules_by_template(request, template_id: int):
    try:
        rules = ShiftRuleManager.get_shift_rule_by_template_id(template_id)
        rules_serialized = ShiftRuleManager.check_db_return(rules, ShiftRuleSerializer)

        return Response(
            {"count": len(rules), "results": rules_serialized},
            status=status.HTTP_200_OK,
        )
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- GET /api/shift-rules/{rule_id} ---
@extend_schema(
    operation_id="shift_rule_retrieve",
    tags=["Shifts · Manager · Rule"],
    summary="Récupérer une ShiftRule (manager)",
    description="Retourne les détails d’une règle (weekday, durée, assignations, exceptions).",
    responses={
        200: OpenApiResponse(
            description="Détail d’une règle",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "id": 31,
                        "template_id": 12,
                        "weekday": 2,
                        "start_local_time": "08:00:00",
                        "duration_minutes": 480,
                        "effective_from": "2025-10-01",
                        "effective_to": None,
                        "apply_to_whole_team": True,
                        "assigned_user_ids": [],
                        "exceptions": [
                            {
                                "id": 7,
                                "date": "2025-10-15",
                                "is_skipped": True,
                                "override_start_local_time": None,
                                "override_duration_minutes": None,
                                "note": "Férié local",
                            }
                        ],
                    },
                )
            ],
        ),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftRule introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="rule_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeamManager])
def retrieve_shift_rule(request, rule_id: int):
    try:
        rule = ShiftRuleManager.get_shift_rule_by_id(rule_id)
        rule_serialized = ShiftRuleManager.check_db_return(rule, ShiftRuleSerializer)

        # Récupérer les exceptions triées pour CETTE règle
        ex_qs = ShiftExceptionManager.get_shift_exception_by_rule_id(
            rule_id=rule.id
        ).order_by("date")
        ex_serialized = ShiftExceptionManager.check_db_return(
            ex_qs, ShiftExceptionSerializer
        )

        # Attacher au dict de la règle
        rule_serialized["exceptions"] = ex_serialized

        return Response(rule_serialized, status=status.HTTP_200_OK)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- 2) POST /api/shift-templates/{template_id}/rules/ ---


@extend_schema(
    operation_id="shift_rule_create",
    tags=["Shifts · Manager · Rule"],
    summary="Ajouter une règle récurrente (manager)",
    description=(
        "Ajoute une **ShiftRule** hebdomadaire (weekday 0=lundi..6=dimanche), avec période d'effet, "
        "heures locales et affectation (toute l'équipe ou liste d'utilisateurs)."
    ),
    request=CreateRuleInput,
    responses={
        201: OpenApiResponse(
            description="Règle créée",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "id": 31,
                        "template_id": 12,
                        "weekday": 2,
                        "start_local_time": "08:00:00",
                        "duration_minutes": 480,
                        "effective_from": "2025-10-01",
                        "effective_to": None,
                        "apply_to_whole_team": True,
                        "assigned_user_ids": [],
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftTemplate introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="template_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeamManager])
def add_shift_rule(request, template_id: int):
    try:
        tpl = ShiftTemplateManager.get_shift_template_by_id(template_id)

        serializer = CreateRuleInput(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = serializer.validated_data
        res = ShiftRuleRepository.create_rule(
            template_id=template_id,
            weekday=payload["weekday"],
            start_local_time=payload["start_local_time"],
            duration_minutes=payload["duration_minutes"],
            effective_from=payload["effective_from"],
            effective_to=payload.get("effective_to"),
            apply_to_whole_team=payload.get("apply_to_whole_team", False),
            assigned_user_ids=payload.get("assigned_user_ids"),
        )

        res_serialized = ShiftRuleManager.check_db_return(res, ShiftRuleSerializer)

        return Response(res_serialized, status=status.HTTP_201_CREATED)

    except APIException as e:
        return Response(e.detail, status=e.status_code)


@extend_schema(
    operation_id="shift_rule_delete",
    tags=["Shifts · Manager · Rule"],
    summary="Supprimer une règle (manager)",
    description="Supprime définitivement une **ShiftRule** donnée.",
    responses={
        204: OpenApiResponse(description="Règle supprimée"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftRule introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="rule_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeamManager])
def delete_shift_rule(request, rule_id: str):
    try:
        res = ShiftRuleManager.delete_rule(rule_id=rule_id)
        if isinstance(res, dict) and "error" in res:
            return Response(res, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- 3) POST /api/shift-rules/{rule_id}/assign-users/ ---


@extend_schema(
    operation_id="shift_rule_assign_users",
    tags=["Shifts · Manager · Rule"],
    summary="Assigner des utilisateurs à une règle (manager)",
    description=(
        "Définit l'affectation d'une **ShiftRule** : soit `apply_to_whole_team=true`, soit une liste `user_ids`.\n"
        "Met automatiquement `apply_to_whole_team=false` en cas d'envoi de `user_ids`."
    ),
    request=AssignUsersInput,
    responses={
        200: OpenApiResponse(
            description="Affectation mise à jour",
            examples=[
                OpenApiExample(
                    "Whole team",
                    value={
                        "id": 31,
                        "template_id": 12,
                        "apply_to_whole_team": True,
                        "assigned_user_ids": [],
                    },
                ),
                OpenApiExample(
                    "Subset users",
                    value={
                        "id": 31,
                        "template_id": 12,
                        "apply_to_whole_team": False,
                        "assigned_user_ids": [8, 9],
                    },
                ),
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / users introuvables"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftRule introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="rule_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeamManager])
def assign_rule_users(request, rule_id: int):
    try:
        rule = ShiftRuleManager.get_shift_rule_by_id(rule_id)
        team_id = rule.template.team_id

        serializer = AssignUsersInput(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = serializer.validated_data
        if payload.get("apply_to_whole_team") is True:
            # activer whole team et vider les assignations spécifiques
            upd = ShiftRuleManager.update_rule(rule.id, apply_to_whole_team=True)
            upd_serialized = ShiftRuleManager.check_db_return(upd, ShiftRuleSerializer)
            cleared = ShiftRuleManager.clear_assigned_users(rule.id)

            if isinstance(cleared, dict) and "error" in cleared:
                return Response(cleared, status=status.HTTP_400_BAD_REQUEST)

            rule.refresh_from_db()

        else:
            # définir user_ids (et forcer apply_to_whole_team=False)
            user_ids = payload.get("user_ids", [])

            res = ShiftRuleManager.assign_users(rule.id, user_ids)
            if isinstance(res, dict) and "error" in res:
                return Response(res, status=status.HTTP_400_BAD_REQUEST)
            rule = res

        return Response(
            {
                "id": rule.id,
                "template_id": rule.template_id,
                "apply_to_whole_team": rule.apply_to_whole_team,
                "assigned_user_ids": list(
                    rule.assigned_users.values_list("id", flat=True)
                ),
            },
            status=status.HTTP_200_OK,
        )

    except APIException as e:
        return Response(e.detail, status=e.status_code)


@extend_schema(
    operation_id="list_shift_exception",
    tags=["Shifts · Manager · Exception"],
    summary="Lister les exceptions d'un shift (manager)",
    description=("Récupère toutes les **ShiftException** pour une règle donnée."),
    request=CreateExceptionInput,
    responses={
        200: OpenApiResponse(
            description="Liste des exceptions",
            examples=[
                OpenApiExample(
                    "Skip",
                    value={
                        "id": 7,
                        "rule": 31,
                        "date": "2025-10-15",
                        "is_skipped": True,
                        "override_start_local_time": None,
                        "override_duration_minutes": None,
                        "note": "Férié local",
                    },
                ),
                OpenApiExample(
                    "Override",
                    value={
                        "id": 8,
                        "rule": 31,
                        "date": "2025-10-14",
                        "is_skipped": False,
                        "override_start_local_time": "10:00:00",
                        "override_duration_minutes": 300,
                        "note": "Réunion matin",
                    },
                ),
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / doublon (rule+date)"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftRule introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="rule_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeamManager])
def list_shift_exception(request):
    try:
        serializer = CreateExceptionInput(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = serializer.validated_data

        res = ShiftExceptionManager.list_exceptions()
        if isinstance(res, dict) and "error" in res:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if res["error"] == "ShiftRule not found"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(res, status=status_code)

        res_serialized = ShiftExceptionManager.check_db_return(
            res, ShiftExceptionSerializer
        )

        return Response(res_serialized, status=status.HTTP_200_OK)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- 4) POST /api/shift-rules/{rule_id}/exceptions/ ---


@extend_schema(
    operation_id="shift_rule_add_exception",
    tags=["Shifts · Manager · Exception"],
    summary="Ajouter une exception sur une date (manager)",
    description=(
        "Crée une **ShiftException** pour une date précise : soit `is_skipped=true` (on saute), "
        "soit override des horaires (`override_start_local_time`, `override_duration_minutes`)."
    ),
    request=CreateExceptionInput,
    responses={
        201: OpenApiResponse(
            description="Exception créée",
            examples=[
                OpenApiExample(
                    "Skip",
                    value={
                        "id": 7,
                        "rule": 31,
                        "date": "2025-10-15",
                        "is_skipped": True,
                        "override_start_local_time": None,
                        "override_duration_minutes": None,
                        "note": "Férié local",
                    },
                ),
                OpenApiExample(
                    "Override",
                    value={
                        "id": 8,
                        "rule": 31,
                        "date": "2025-10-14",
                        "is_skipped": False,
                        "override_start_local_time": "10:00:00",
                        "override_duration_minutes": 300,
                        "note": "Réunion matin",
                    },
                ),
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / doublon (rule+date)"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftRule introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="rule_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeamManager])
def add_shift_exception(request, rule_id: int):
    try:
        serializer = CreateExceptionInput(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = serializer.validated_data

        res = ShiftExceptionManager.create_exception(
            rule_id=rule_id,
            date=payload["date"],
            is_skipped=payload.get("is_skipped", False),
            override_start_local_time=payload.get("override_start_local_time"),
            override_duration_minutes=payload.get("override_duration_minutes"),
            note=payload.get("note", "") or "",
        )
        if isinstance(res, dict) and "error" in res:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if res["error"] == "ShiftRule not found"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(res, status=status_code)

        res_serialized = ShiftExceptionManager.check_db_return(
            res, ShiftExceptionSerializer
        )

        return Response(res_serialized, status=status.HTTP_201_CREATED)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


@extend_schema(
    operation_id="shift_exception_update",
    tags=["Shifts · Manager · Exception"],
    summary="Mettre à jour une exception (manager)",
    description="Modifie une **ShiftException** existante.",
    request=UpdateExceptionInput,
    responses={
        200: OpenApiResponse(
            description="Exception mise à jour",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "id": 7,
                        "rule": 31,
                        "date": "2025-10-15",
                        "is_skipped": False,
                        "override_start_local_time": "09:00:00",
                        "override_duration_minutes": 420,
                        "note": "Horaire ajusté",
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / conflit"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftException introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="exception_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeamManager])
def update_shift_exception(request, exception_id: str):
    try:
        serializer = UpdateExceptionInput(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = serializer.validated_data

        res = ShiftExceptionManager.update_exception(
            exception_id=exception_id,
            date=payload["date"],
            is_skipped=payload.get("is_skipped", False),
            override_start_local_time=payload.get("override_start_local_time"),
            override_duration_minutes=payload.get("override_duration_minutes"),
            note=payload.get("note", "") or "",
        )
        if isinstance(res, dict) and "error" in res:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if res["error"] == "ShiftException not found"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(res, status=status_code)

        res_serialized = ShiftExceptionManager.check_db_return(
            res, ShiftExceptionSerializer
        )

        return Response(res_serialized, status=status.HTTP_200_OK)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


@extend_schema(
    operation_id="shift_exception_delete",
    tags=["Shifts · Manager · Exception"],
    summary="Supprimer une exception (manager)",
    description="Supprime définitivement une **ShiftException** donnée.",
    responses={
        204: OpenApiResponse(description="Exception supprimée"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftException introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="exception_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
    ],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeamManager])
def delete_shift_exception(request, exception_id: str):
    try:
        res = ShiftExceptionManager.delete_exception(exception_id=exception_id)
        if isinstance(res, dict) and "error" in res:
            return Response(res, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- 5) POST /api/teams/{team_id}/shifts/generate?days=56 ---


@extend_schema(
    operation_id="shift_generate_occurrences",
    tags=["Shifts · Manager · Rule"],
    summary="Générer les occurrences de shifts (manager)",
    description=(
        "Génère les **Shifts** concrets à partir des règles de l'équipe pour une fenêtre future (rolling window). "
        "La génération est idempotente (pas de doublons)."
    ),
    responses={
        200: OpenApiResponse(
            description="OK",
            examples=[OpenApiExample("Succès", value={"created": 24})],
        ),
        400: OpenApiResponse(description="Paramètre `days` invalide"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
    },
    parameters=[
        OpenApiParameter(
            name="team_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
        OpenApiParameter(
            name="days",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Nombre de jours à générer (1..365). Par défaut 56.",
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeamManager])
def generate_team_shifts(request, team_id: int):
    try:
        days_param = request.query_params.get("days")
        if days_param:
            days = ShiftManager.check_query_param_element_int(request, "days")
        else:
            days = 56

        if days < 1 or days > 365:
            return Response(
                {"error": "days must be in [1..365]"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except ValueError:
        return Response(
            {"error": "days must be integer"}, status=status.HTTP_400_BAD_REQUEST
        )

    today = date.today()
    res = generate_occurrences_for_window(
        today, today + timedelta(days=days), team_id=team_id
    )

    return Response({"created": res.get("created", 0)}, status=status.HTTP_200_OK)


# --- 6) GET /api/users/{user_id}/shifts?from=...&to=... ---


@extend_schema(
    operation_id="user_shifts_list_window",
    tags=["Shifts · Runtime"],
    summary="Lister les shifts d'un utilisateur (fenêtre temporelle)",
    description=(
        "Retourne les **occurrences** de shifts pour un utilisateur entre `from` et `to` (ISO 8601). "
        "Autorisé pour l'utilisateur lui-même ou le manager de son équipe."
    ),
    responses={
        200: OpenApiResponse(
            description="Liste des shifts",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "count": 2,
                        "results": [
                            {
                                "id": 101,
                                "user_id": 8,
                                "start_time": "2025-10-14T08:00:00+00:00",
                                "end_time": "2025-10-14T16:00:00+00:00",
                                "template_id": 12,
                                "rule_id": 31,
                                "real_start_time": None,
                                "real_end_time": None,
                            },
                            {
                                "id": 111,
                                "user_id": 8,
                                "start_time": "2025-10-16T08:00:00+00:00",
                                "end_time": "2025-10-16T16:00:00+00:00",
                                "template_id": 12,
                                "rule_id": 31,
                                "real_start_time": "2025-10-16T08:03:12+00:00",
                                "real_end_time": "2025-10-16T15:59:41+00:00",
                            },
                        ],
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Paramètres `from`/`to` invalides"),
        403: OpenApiResponse(description="Interdit"),
        404: OpenApiResponse(description="Utilisateur introuvable"),
    },
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
        OpenApiParameter(
            name="from",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Datetime ISO 8601, ex: 2025-10-13T00:00:00Z",
        ),
        OpenApiParameter(
            name="to",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Datetime ISO 8601, ex: 2025-10-19T23:59:59Z",
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_user_shifts_window(request, user_id: int):
    try:
        # Autz: le user lui-même OU le manager de son équipe
        target = UserManager.get_user_by_id(user_id)

        # fenêtre
        try:
            from_str = ShiftManager.check_query_param_element_str(request, "from")
            to_str = ShiftManager.check_query_param_element_str(request, "to")
            if not from_str or not to_str:
                return Response(
                    {"error": "Query params 'from' and 'to' are required (ISO dates)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            start = ShiftManager.parse_iso_query_datetime(from_str)
            end = ShiftManager.parse_iso_query_datetime(to_str)

            if end <= start:
                return Response(
                    {"error": "'to' must be after 'from'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception:
            return Response(
                {"error": "Invalid 'from'/'to' format. Use ISO 8601."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = ShiftManager.list_shifts_by_user_id_and_date(user_id, start=start, end=end)
        qs_serialized = ShiftManager.check_db_return(qs, ShiftSerializer)

        return Response(
            {"count": len(qs), "results": qs_serialized}, status=status.HTTP_200_OK
        )
    except APIException as e:
        return Response(e.detail, status=e.status_code)


# --- 7) (optionnel) GET /api/teams/{team_id}/calendar?from=...&to=... ---


@extend_schema(
    operation_id="team_calendar",
    tags=["Shifts · Manager · Rule"],
    summary="Calendrier agrégé de l’équipe (fenêtre temporelle, ISO)",
    description=(
        "Retourne les **occurrences** de l’équipe entre `from` et `to` (ISO 8601) avec "
        "`user_email`, `template_id`, `rule_id`. Accès réservé aux managers de l’équipe."
    ),
    responses={
        200: OpenApiResponse(
            description="Calendrier d’équipe",
            examples=[
                OpenApiExample(
                    "Succès",
                    value={
                        "team_id": 4,
                        "from": "2025-10-13T00:00:00+00:00",
                        "to": "2025-10-19T23:59:59+00:00",
                        "count": 2,
                        "results": [
                            {
                                "shift_id": 101,
                                "user_id": 8,
                                "user_email": "emma@team.com",
                                "start_time": "2025-10-14T08:00:00+00:00",
                                "end_time": "2025-10-14T16:00:00+00:00",
                                "template_id": 12,
                                "rule_id": 31,
                            },
                            {
                                "shift_id": 102,
                                "user_id": 9,
                                "user_email": "lucas@team.com",
                                "start_time": "2025-10-15T08:00:00+00:00",
                                "end_time": "2025-10-15T16:00:00+00:00",
                                "template_id": 12,
                                "rule_id": 31,
                            },
                        ],
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Paramètres `from`/`to` invalides"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
    },
    parameters=[
        OpenApiParameter(
            name="team_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        ),
        OpenApiParameter(
            name="from",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Datetime ISO 8601, ex: 2025-10-13T00:00:00Z",
        ),
        OpenApiParameter(
            name="to",
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Datetime ISO 8601, ex: 2025-10-19T23:59:59Z",
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeamManager])
def team_calendar_view(request, team_id: int):
    try:
        try:
            from_str = ShiftManager.check_query_param_element_str(request, "from")
            to_str = ShiftManager.check_query_param_element_str(request, "to")

            if not from_str or not to_str:
                return Response(
                    {"error": "Query params 'from' and 'to' are required (ISO)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            start = ShiftManager.parse_iso_query_datetime(from_str)
            end = ShiftManager.parse_iso_query_datetime(to_str)
            if end <= start:
                return Response(
                    {"error": "'to' must be after 'from'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        shifts = ShiftManager.list_shifts_by_team_id(
            team_id, from_date=start, to_date=end
        )
        shifts_serialized = ShiftManager.check_db_return(shifts, ShiftSerializer)
        team_serialized = {
            "team_id": team_id,
            "from": start,
            "to": end,
            "count": len(shifts),
            "results": shifts_serialized,
        }

        return Response(team_serialized, status=status.HTTP_200_OK)
    except APIException as e:
        return Response(e.detail, status=e.status_code)
