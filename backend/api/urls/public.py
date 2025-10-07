from django.urls import path
from api.views.public import health

urlpatterns = [
    path("health/", health, name="health"),
]