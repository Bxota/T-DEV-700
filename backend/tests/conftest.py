import pytest
from datetime import timedelta, timezone, datetime

from model_bakery import baker

from django.contrib.auth import get_user_model
from datetime import timezone

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from db_manager.models import Roles

User = get_user_model()

@pytest.fixture
def manager_role(db):
    # S'assure que le rôle 'manager' existe pour que la permission ne lève pas DoesNotExist
    Roles.objects.get_or_create(name="manager")
    return True


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    role = baker.make("db_manager.Roles", name="employee")
    return baker.make(User, email="alice@example.com", is_active=True, role=role)

@pytest.fixture
def manager():
    role = baker.make("db_manager.Roles", name="manager")
    return baker.make(User, email="manager@example.com", is_active=True, is_staff=True, role=role)

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
    return baker.make("db_manager.Teams", name="Ops")

@pytest.fixture
def user_in_team(user, team):
    # selon ton modèle relationnel
    team.members.add(user)
    return user

@pytest.fixture
def clock(user):
    return baker.make("shifts.Clock", user=user, clock_in=timezone.now())