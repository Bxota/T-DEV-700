import pytest
from datetime import timedelta, timezone, datetime

from model_bakery import baker

from django.contrib.auth import get_user_model
from datetime import timezone

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return baker.make(User, email="alice@example.com", is_active=True)

@pytest.fixture
def manager():
    return baker.make(User, email="manager@example.com", is_active=True, is_staff=True)

@pytest.fixture
def auth_headers(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

@pytest.fixture
def manager_headers(manager):
    refresh = RefreshToken.for_user(manager)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

@pytest.fixture
def expired_headers(user, settings):
    settings.SIMPLE_JWT["VERIFY_EXP"] = True
    settings.SIMPLE_JWT["LEEWAY"] = 0

    token = AccessToken.for_user(user)
    token.set_exp(from_time=datetime.now(timezone.utc) - timedelta(days=60))

    return {"HTTP_AUTHORIZATION": f"Bearer {str(token)}"}

# Exemples de factories rapides
@pytest.fixture
def team():
    return baker.make("teams.Team", name="Ops")

@pytest.fixture
def user_in_team(user, team):
    # selon ton modèle relationnel
    team.members.add(user)
    return user

@pytest.fixture
def clock(user):
    return baker.make("shifts.Clock", user=user, clock_in=timezone.now())