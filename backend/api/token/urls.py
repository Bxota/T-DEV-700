from django.urls import path

from api.token.views import whoami

urlpatterns = [
    path("token/whoami/", whoami, name="whoami"),
]
    