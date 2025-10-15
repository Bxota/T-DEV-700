# api/shifts/views_manager.py
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from db_manager.models import Users, Teams, Shifts, ShiftTemplate, ShiftRule
from db_manager.repositories.shift_template_repository import ShiftTemplateRepository
from db_manager.repositories.shift_rule_repository import ShiftRuleRepository
from db_manager.repositories.shift_exception_repository import ShiftExceptionRepository

from api.shifts.shift_gestion.serializer import (
    CreateTemplateInput, CreateRuleInput, AssignUsersInput, CreateExceptionInput
)
from api.shifts.generator import generate_occurrences_for_window

from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
)
from drf_spectacular.types import OpenApiTypes

# --- Helpers de permission ---

def _is_manager_of_team(user: Users, team_id: int) -> bool:
    try:
        if not user.is_active:
            return False
        if user.team_id != team_id:
            return False
        # Si ton "role" a un champ 'name', on compare à "manager"
        return (user.role and user.role.name.lower() == "manager")
    except Exception:
        return False

def _ensure_manager_of_team(user: Users, team_id: int):
    if not _is_manager_of_team(user, team_id):
        return Response({"error": "Forbidden (manager-only for this team)."}, status=status.HTTP_403_FORBIDDEN)
    return None

# --- 1) POST /api/teams/{team_id}/shift-templates/ ---

@extend_schema(
    operation_id="shift_template_create",
    tags=["Shifts · Manager"],
    summary="Créer un modèle de shift (manager)",
    description="Crée un **ShiftTemplate** pour l’équipe donnée. Accès réservé aux managers de l’équipe.",
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
                        "is_active": True
                    }
                )
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / Conflit"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
    },
    parameters=[
        OpenApiParameter(name="team_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_shift_template(request, team_id: int):
    guard = _ensure_manager_of_team(request.user, team_id)
    if guard:
        return guard

    serializer = CreateTemplateInput(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    payload = serializer.validated_data
    res = ShiftTemplateRepository.create_template(
        name=payload["name"],
        team_id=team_id,
        created_by_id=request.user.id,
        default_duration_minutes=payload["default_duration_minutes"],
        timezone=payload.get("timezone", "Europe/Paris"),
        role_id=payload.get("role_id"),
        is_active=payload.get("is_active", True),
    )
    if isinstance(res, dict) and "error" in res:
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    # réponse simple
    return Response({
        "id": res.id,
        "name": res.name,
        "team_id": res.team_id,
        "role_id": res.role_id,
        "default_duration_minutes": res.default_duration_minutes,
        "timezone": res.timezone,
        "is_active": res.is_active,
    }, status=status.HTTP_201_CREATED)

# --- 2) POST /api/shift-templates/{template_id}/rules/ ---

@extend_schema(
    operation_id="shift_rule_create",
    tags=["Shifts · Manager"],
    summary="Ajouter une règle récurrente (manager)",
    description=(
        "Ajoute une **ShiftRule** hebdomadaire (weekday 0=lundi..6=dimanche), avec période d’effet, "
        "heures locales et affectation (toute l’équipe ou liste d’utilisateurs)."
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
                        "assigned_user_ids": []
                    }
                )
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftTemplate introuvable"),
    },
    parameters=[
        OpenApiParameter(name="template_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_shift_rule(request, template_id: int):
    tpl = ShiftTemplate.objects.filter(id=template_id).select_related("team").first()
    if not tpl:
        return Response({"error": "ShiftTemplate not found"}, status=status.HTTP_404_NOT_FOUND)

    guard = _ensure_manager_of_team(request.user, tpl.team_id)
    if guard:
        return guard

    serializer = CreateRuleInput(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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
    if isinstance(res, dict) and "error" in res:
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "id": res.id,
        "template_id": res.template_id,
        "weekday": res.weekday,
        "start_local_time": res.start_local_time,
        "duration_minutes": res.duration_minutes,
        "effective_from": res.effective_from,
        "effective_to": res.effective_to,
        "apply_to_whole_team": res.apply_to_whole_team,
        "assigned_user_ids": list(res.assigned_users.values_list("id", flat=True)),
    }, status=status.HTTP_201_CREATED)

# --- 3) POST /api/shift-rules/{rule_id}/assign-users/ ---

@extend_schema(
    operation_id="shift_rule_assign_users",
    tags=["Shifts · Manager"],
    summary="Assigner des utilisateurs à une règle (manager)",
    description=(
        "Définit l’affectation d’une **ShiftRule** : soit `apply_to_whole_team=true`, soit une liste `user_ids`.\n"
        "Met automatiquement `apply_to_whole_team=false` en cas d’envoi de `user_ids`."
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
                        "assigned_user_ids": []
                    }
                ),
                OpenApiExample(
                    "Subset users",
                    value={
                        "id": 31,
                        "template_id": 12,
                        "apply_to_whole_team": False,
                        "assigned_user_ids": [8, 9]
                    }
                ),
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / users introuvables"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftRule introuvable"),
    },
    parameters=[
        OpenApiParameter(name="rule_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_rule_users(request, rule_id: int):
    rule = ShiftRule.objects.filter(id=rule_id).select_related("template__team").first()
    if not rule:
        return Response({"error": "ShiftRule not found"}, status=status.HTTP_404_NOT_FOUND)

    team_id = rule.template.team_id
    guard = _ensure_manager_of_team(request.user, team_id)
    if guard:
        return guard

    serializer = AssignUsersInput(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    payload = serializer.validated_data
    if payload.get("apply_to_whole_team") is True:
        # activer whole team et vider les assignations spécifiques
        upd = ShiftRuleRepository.update_rule(rule.id, apply_to_whole_team=True)
        if isinstance(upd, dict) and "error" in upd:
            return Response(upd, status=status.HTTP_400_BAD_REQUEST)
        cleared = ShiftRuleRepository.clear_assigned_users(rule.id)
        if isinstance(cleared, dict) and "error" in cleared:
            return Response(cleared, status=status.HTTP_400_BAD_REQUEST)
        rule.refresh_from_db()
    else:
        # définir user_ids (et forcer apply_to_whole_team=False)
        user_ids = payload.get("user_ids", [])
        res = ShiftRuleRepository.assign_users(rule.id, user_ids)
        if isinstance(res, dict) and "error" in res:
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        rule = res

    return Response({
        "id": rule.id,
        "template_id": rule.template_id,
        "apply_to_whole_team": rule.apply_to_whole_team,
        "assigned_user_ids": list(rule.assigned_users.values_list("id", flat=True)),
    }, status=status.HTTP_200_OK)

# --- 4) POST /api/shift-rules/{rule_id}/exceptions/ ---

@extend_schema(
    operation_id="shift_rule_add_exception",
    tags=["Shifts · Manager"],
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
                        "rule_id": 31,
                        "date": "2025-10-15",
                        "is_skipped": True,
                        "override_start_local_time": None,
                        "override_duration_minutes": None,
                        "note": "Férié local"
                    }
                ),
                OpenApiExample(
                    "Override",
                    value={
                        "id": 8,
                        "rule_id": 31,
                        "date": "2025-10-14",
                        "is_skipped": False,
                        "override_start_local_time": "10:00:00",
                        "override_duration_minutes": 300,
                        "note": "Réunion matin"
                    }
                ),
            ],
        ),
        400: OpenApiResponse(description="Erreur de validation / doublon (rule+date)"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
        404: OpenApiResponse(description="ShiftRule introuvable"),
    },
    parameters=[
        OpenApiParameter(name="rule_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_shift_exception(request, rule_id: int):
    rule = ShiftRule.objects.filter(id=rule_id).select_related("template__team").first()
    if not rule:
        return Response({"error": "ShiftRule not found"}, status=status.HTTP_404_NOT_FOUND)

    team_id = rule.template.team_id
    guard = _ensure_manager_of_team(request.user, team_id)
    if guard:
        return guard

    serializer = CreateExceptionInput(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    payload = serializer.validated_data
    res = ShiftExceptionRepository.create_exception(
        rule_id=rule_id,
        date_value=payload["date"],
        is_skipped=payload.get("is_skipped", False),
        override_start_local_time=payload.get("override_start_local_time"),
        override_duration_minutes=payload.get("override_duration_minutes"),
        note=payload.get("note", "") or "",
    )
    if isinstance(res, dict) and "error" in res:
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "id": res.id,
        "rule_id": res.rule_id,
        "date": res.date,
        "is_skipped": res.is_skipped,
        "override_start_local_time": res.override_start_local_time,
        "override_duration_minutes": res.override_duration_minutes,
        "note": res.note,
    }, status=status.HTTP_201_CREATED)

# --- 5) POST /api/teams/{team_id}/shifts/generate?days=56 ---

@extend_schema(
    operation_id="shift_generate_occurrences",
    tags=["Shifts · Manager"],
    summary="Générer les occurrences de shifts (manager)",
    description=(
        "Génère les **Shifts** concrets à partir des règles de l’équipe pour une fenêtre future (rolling window). "
        "La génération est idempotente (pas de doublons)."
    ),
    responses={
        200: OpenApiResponse(
            description="OK",
            examples=[
                OpenApiExample("Succès", value={"created": 24})
            ],
        ),
        400: OpenApiResponse(description="Paramètre `days` invalide"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
    },
    parameters=[
        OpenApiParameter(name="team_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
        OpenApiParameter(
            name="days", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
            description="Nombre de jours à générer (1..365). Par défaut 56."
        ),
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_team_shifts(request, team_id: int):
    guard = _ensure_manager_of_team(request.user, team_id)
    if guard:
        return guard

    try:
        days = int(request.query_params.get("days", "56"))
        if days < 1 or days > 365:
            return Response({"error": "days must be in [1..365]"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"error": "days must be integer"}, status=status.HTTP_400_BAD_REQUEST)

    today = date.today()
    res = generate_occurrences_for_window(today, today + timedelta(days=days), team_id=team_id)
    return Response({"created": res.get("created", 0)}, status=status.HTTP_200_OK)

# --- 6) GET /api/users/{user_id}/shifts?from=...&to=... ---

@extend_schema(
    operation_id="user_shifts_list_window",
    tags=["Shifts · Runtime"],
    summary="Lister les shifts d’un utilisateur (fenêtre temporelle)",
    description=(
        "Retourne les **occurrences** de shifts pour un utilisateur entre `from` et `to` (ISO 8601). "
        "Autorisé pour l’utilisateur lui-même ou le manager de son équipe."
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
                                "real_end_time": None
                            },
                            {
                                "id": 111,
                                "user_id": 8,
                                "start_time": "2025-10-16T08:00:00+00:00",
                                "end_time": "2025-10-16T16:00:00+00:00",
                                "template_id": 12,
                                "rule_id": 31,
                                "real_start_time": "2025-10-16T08:03:12+00:00",
                                "real_end_time": "2025-10-16T15:59:41+00:00"
                            }
                        ]
                    }
                )
            ],
        ),
        400: OpenApiResponse(description="Paramètres `from`/`to` invalides"),
        403: OpenApiResponse(description="Interdit"),
        404: OpenApiResponse(description="Utilisateur introuvable"),
    },
    parameters=[
        OpenApiParameter(name="user_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
        OpenApiParameter(name="from", type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY, required=True,
                         description="Datetime ISO 8601, ex: 2025-10-13T00:00:00Z"),
        OpenApiParameter(name="to", type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY, required=True,
                         description="Datetime ISO 8601, ex: 2025-10-19T23:59:59Z"),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_user_shifts_window(request, user_id: int):
    # Autz: le user lui-même OU le manager de son équipe
    target = Users.objects.filter(id=user_id).first()
    if not target:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    is_self = (request.user.id == user_id)
    is_mgr_same_team = (_is_manager_of_team(request.user, target.team_id) if target.team_id else False)
    if not (is_self or is_mgr_same_team):
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    # fenêtre
    try:
        from_str = request.query_params.get("from")
        to_str = request.query_params.get("to")
        if not from_str or not to_str:
            return Response({"error": "Query params 'from' and 'to' are required (ISO dates)."}, status=status.HTTP_400_BAD_REQUEST)
        start = timezone.datetime.fromisoformat(from_str)
        end = timezone.datetime.fromisoformat(to_str)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if end <= start:
            return Response({"error": "'to' must be after 'from'."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "Invalid 'from'/'to' format. Use ISO 8601."}, status=status.HTTP_400_BAD_REQUEST)

    qs = Shifts.objects.filter(
        user_id=user_id,
        start_time__lt=end,
        end_time__gt=start
    ).order_by("start_time")

    data = [{
        "id": s.id,
        "user_id": s.user_id,
        "start_time": s.start_time,
        "end_time": s.end_time,
        "template_id": s.template_id,
        "rule_id": s.rule_id,
        "real_start_time": s.real_start_time,
        "real_end_time": s.real_end_time,
    } for s in qs]

    return Response({"count": len(data), "results": data}, status=status.HTTP_200_OK)

# --- 7) (optionnel) GET /api/teams/{team_id}/calendar?from=...&to=... ---

@extend_schema(
    operation_id="team_calendar",
    tags=["Shifts · Manager"],
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
                                "rule_id": 31
                            },
                            {
                                "shift_id": 102,
                                "user_id": 9,
                                "user_email": "lucas@team.com",
                                "start_time": "2025-10-15T08:00:00+00:00",
                                "end_time": "2025-10-15T16:00:00+00:00",
                                "template_id": 12,
                                "rule_id": 31
                            }
                        ]
                    }
                )
            ],
        ),
        400: OpenApiResponse(description="Paramètres `from`/`to` invalides"),
        403: OpenApiResponse(description="Interdit (manager requis)"),
    },
    parameters=[
        OpenApiParameter(name="team_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
        OpenApiParameter(name="from", type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY, required=True,
                         description="Datetime ISO 8601, ex: 2025-10-13T00:00:00Z"),
        OpenApiParameter(name="to", type=OpenApiTypes.DATETIME, location=OpenApiParameter.QUERY, required=True,
                         description="Datetime ISO 8601, ex: 2025-10-19T23:59:59Z"),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def team_calendar_view(request, team_id: int):
    # manager only (sinon, expose trop d'infos)
    guard = _ensure_manager_of_team(request.user, team_id)
    if guard:
        return guard

    try:
        from_str = request.query_params.get("from")
        to_str = request.query_params.get("to")
        if not from_str or not to_str:
            return Response({"error": "Query params 'from' and 'to' are required (ISO)."}, status=status.HTTP_400_BAD_REQUEST)
        start = timezone.datetime.fromisoformat(from_str)
        end = timezone.datetime.fromisoformat(to_str)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if end <= start:
            return Response({"error": "'to' must be after 'from'."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "Invalid 'from'/'to' format. Use ISO 8601."}, status=status.HTTP_400_BAD_REQUEST)

    users_ids = list(Users.objects.filter(team_id=team_id, is_active=True).values_list("id", flat=True))
    qs = Shifts.objects.filter(
        user_id__in=users_ids,
        start_time__lt=end,
        end_time__gt=start
    ).select_related("user").order_by("start_time")

    results = [{
        "shift_id": s.id,
        "user_id": s.user_id,
        "user_email": s.user.email if s.user_id else None,
        "start_time": s.start_time,
        "end_time": s.end_time,
        "template_id": s.template_id,
        "rule_id": s.rule_id,
    } for s in qs]

    return Response({
        "team_id": team_id,
        "from": start,
        "to": end,
        "count": len(results),
        "results": results
    }, status=status.HTTP_200_OK)