from django.urls import path

from api.users.shifts.views import list_shifts, shift_off, shift_on

urlpatterns = [
    path("shifts/", list_shifts, name="list_user_shifts"),
    path("shifts/<int:shift_id>/on/", shift_on, name="shift_on"),
    path("shifts/<int:shift_id>/off/", shift_off, name="shift_off"),
]
    