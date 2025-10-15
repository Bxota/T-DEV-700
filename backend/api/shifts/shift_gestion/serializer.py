# api/shifts/serializers_manager.py
from rest_framework import serializers

class CreateTemplateInput(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    default_duration_minutes = serializers.IntegerField(min_value=1)
    timezone = serializers.CharField(max_length=64, default="Europe/Paris")
    role_id = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)

class CreateRuleInput(serializers.Serializer):
    weekday = serializers.IntegerField(min_value=0, max_value=6)  # 0=Mon..6=Sun
    start_local_time = serializers.TimeField()
    duration_minutes = serializers.IntegerField(min_value=1)
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)
    apply_to_whole_team = serializers.BooleanField(default=False)
    assigned_user_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

class AssignUsersInput(serializers.Serializer):
    apply_to_whole_team = serializers.BooleanField(required=False)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

class CreateExceptionInput(serializers.Serializer):
    date = serializers.DateField()
    is_skipped = serializers.BooleanField(default=False)
    override_start_local_time = serializers.TimeField(required=False, allow_null=True)
    override_duration_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    note = serializers.CharField(required=False, allow_blank=True, max_length=255)