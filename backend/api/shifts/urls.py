from django.urls import path

from api.shifts.views import TeamShiftCollection, UserShiftCollection, UserShiftDetail

urlpatterns = [
    path("users/<int:user_id>/shifts/", UserShiftCollection.as_view(), name="user_shifts"),
    path("users/<int:user_id>/shifts/<int:shift_id>", UserShiftDetail.as_view(), name="user_shift"),
    path("teams/<int:team_id>/shifts/", TeamShiftCollection.as_view(), name="team_shifts")
]