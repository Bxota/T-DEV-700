from django.urls import path

from api.token.views import whoami, CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/whoami/", whoami, name="whoami"),
]
    