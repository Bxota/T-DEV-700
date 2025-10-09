from django.urls import path, include

from api.users.views import UserCollection, UserDetail, UserTeamCollection, get_user_reports, get_user_clocks_summary


urlpatterns = [
    path("users/", UserCollection.as_view(), name="users"),
    path("users/<int:user_id>/", UserDetail.as_view(), name="user_detail"),
    path("users/<int:team_id>/", UserTeamCollection.as_view(), name="user"),
    path("users/<int:team_id>/reports", get_user_reports, name="user_reports"),
    path("users/<int:team_id>/clocks", get_user_clocks_summary, name="user_clocks"),
]