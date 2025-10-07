from django.urls import include, path

urlpatterns = [
    path("", include("api.urls.public")),
    path("", include("api.urls.auth"))
]