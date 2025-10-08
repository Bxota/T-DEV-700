from django.urls import path, include

from api.users.views import UserDetail, UserCollection


urlpatterns = [
    path("users/", UserCollection.as_view(), name="users"),
    path("users/<int:user_id>/", UserDetail.as_view(), name="user"),
]