from rest_framework import serializers
from .models import Shifts, Teams, Users, Roles

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shifts
        fields = ("id", "user", "start_time", "end_time", "real_start_time", "real_end_time")

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model =Teams
        fields = ("id", "name")

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ("id", "name")
        
class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Users
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "team",
        )