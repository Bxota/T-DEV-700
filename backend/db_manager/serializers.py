from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import Shifts, Teams, Users, Roles, ShiftTemplate, ShiftRule, ShiftException

from datetime import datetime, timezone

from datetime import datetime, timezone

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
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personnalisé pour ajouter le temps d'expiration"""

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        # Ajouter les tokens
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Ajouter la durée d'expiration (en secondes)
        data['access_token_expires_at'] = (datetime.now(timezone.utc) + refresh.access_token.lifetime).isoformat()
        data['refresh_token_expires_at'] = (datetime.now(timezone.utc) + refresh.lifetime).isoformat()

        return data
    
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """Serializer personnalisé pour ajouter le temps d'expiration du nouvel access token"""

    def validate(self, attrs):
        # Appelle le serializer d'origine -> renvoie { "access": "...", ("refresh": "...") }
        data = super().validate(attrs)

        # Récupérer l'access token renvoyé et en extraire l'exp (epoch)
        access_str = data["access"]
        access = AccessToken(access_str)
        access_exp_ts = int(access["exp"])
        access_expires_at = datetime.fromtimestamp(access_exp_ts, tz=timezone.utc)

        data["access_token_expires_at"] = access_expires_at.isoformat()

        # Si la rotation de refresh est activée, 'data' contient un nouveau refresh -> expose son expiry aussi
        if "refresh" in data:
            refresh = RefreshToken(data["refresh"])
            refresh_exp_ts = int(refresh["exp"])
            data["refresh_token_expires_at"] = datetime.fromtimestamp(refresh_exp_ts, tz=timezone.utc).isoformat()

        return data

class ShiftTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftTemplate
        fields = ["id", "name", "team_id", "role_id", "default_duration_minutes", "timezone", "is_active"]

class ShiftExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftException
        fields = ["id", "rule", "date", "is_skipped", "override_start_local_time", "override_duration_minutes", "note"]

class ShiftRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftRule
        fields = ["id", "template_id", "weekday", "start_local_time", "duration_minutes", 
                  "effective_from", "effective_to", "apply_to_whole_team", "assigned_users"]