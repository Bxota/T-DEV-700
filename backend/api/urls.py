from django.urls import path, include

urlpatterns = [
    path("", include("api.health.urls")),
    path("", include("api.teams.urls")),
    path("", include("api.token.urls")),
    path("", include("api.users.urls")),
    path("", include("api.shifts.urls")),
]
