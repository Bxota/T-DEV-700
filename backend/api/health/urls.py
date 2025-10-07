from django.urls import path

from api.health.views import health_authenticated, health, health_manager

urlpatterns = [
    path("health/", health, name="health"),
    path("health/auth/", health_authenticated, name="health_authenticated"),
    path("health/auth-manager/", health_manager, name="health_manager"),
]
    