from django.urls import path

from api.health.views import health_authenticated, health

urlpatterns = [
    path("health/", health, name="health"),
    path("health/auth/", health_authenticated, name="health_authenticated"),
]
    