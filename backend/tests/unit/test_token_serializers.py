from datetime import datetime, timezone

import pytest
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from db_manager.models import Users, Roles
from db_manager.serializers import CustomTokenRefreshSerializer


@pytest.mark.django_db
def test_custom_token_refresh_serializer_adds_access_exp(monkeypatch):
    role, _ = Roles.objects.get_or_create(name="manager")
    user = Users.objects.create_user(
        email="refresh@example.com",
        password="pwd",
        first_name="Re",
        last_name="Fresh",
        role=role,
    )

    refresh = RefreshToken.for_user(user)
    access_str = str(refresh.access_token)

    def fake_validate(self, attrs):
        return {"access": access_str}

    monkeypatch.setattr(TokenRefreshSerializer, "validate", fake_validate)

    serializer = CustomTokenRefreshSerializer()
    result = serializer.validate({"refresh": str(refresh)})

    expected = datetime.fromtimestamp(refresh.access_token["exp"], tz=timezone.utc).isoformat()
    assert result["access_token_expires_at"] == expected
    assert "refresh_token_expires_at" not in result


@pytest.mark.django_db
def test_custom_token_refresh_serializer_adds_refresh_exp_when_present(monkeypatch):
    role, _ = Roles.objects.get_or_create(name="manager")
    user = Users.objects.create_user(
        email="refresh2@example.com",
        password="pwd",
        first_name="Re",
        last_name="FreshTwo",
        role=role,
    )

    refresh = RefreshToken.for_user(user)
    access_str = str(refresh.access_token)
    refresh_str = str(refresh)

    def fake_validate(self, attrs):
        return {"access": access_str, "refresh": refresh_str}

    monkeypatch.setattr(TokenRefreshSerializer, "validate", fake_validate)

    serializer = CustomTokenRefreshSerializer()
    result = serializer.validate({"refresh": refresh_str})

    expected_access = datetime.fromtimestamp(refresh.access_token["exp"], tz=timezone.utc).isoformat()
    expected_refresh = datetime.fromtimestamp(refresh["exp"], tz=timezone.utc).isoformat()

    assert result["access_token_expires_at"] == expected_access
    assert result["refresh_token_expires_at"] == expected_refresh
