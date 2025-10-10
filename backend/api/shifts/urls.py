from django.urls import path

from api.shifts.views import TeamShiftCollection, UserShiftCollection, UserShiftDetail, user_shift_check_in, user_shift_check_out

urlpatterns = [
    path("users/<int:user_id>/shifts/", UserShiftCollection.as_view(), name="user_shifts"),
    path("users/<int:user_id>/shifts/<int:shift_id>/", UserShiftDetail.as_view(), name="user_shift"),
    path("users/<int:user_id>/shifts/<int:shift_id>/check-in/", user_shift_check_in, name="user_shift_check_in"),
    path("users/<int:user_id>/shifts/<int:shift_id>/check-out/", user_shift_check_out, name="user_shift_check_out"),
    path("teams/<int:team_id>/shifts/", TeamShiftCollection.as_view(), name="team_shifts")
]