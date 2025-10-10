from rest_framework import serializers
from .models import Shifts

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shifts
        fields = ("id", "user", "start_time", "end_time")