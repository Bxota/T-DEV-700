from django.urls import path, include

from api.users.views import UserDetail, UserCollection, get_user_reports


urlpatterns = [
    path("users/", UserCollection.as_view(), name="users"),
    path("users/<int:user_id>/", UserDetail.as_view(), name="user"),
    path("users/<int:user_id>/reports", get_user_reports, name="user_reports"),
]