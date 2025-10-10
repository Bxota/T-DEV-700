from rest_framework import serializers
from .models import Shifts, Teams

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shifts
        fields = ("id", "user", "start_time", "end_time", "real_start_time", "real_end_time")

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model =Teams
        fields = ("id", "name")