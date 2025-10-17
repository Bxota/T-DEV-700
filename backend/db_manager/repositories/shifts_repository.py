from datetime import datetime

from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import APIException

from db_manager.models import Shifts


def _ensure_datetime(value):
    if isinstance(value, str):
        parsed = parse_datetime(value)
        if parsed is None and value.endswith("Z"):
            parsed = parse_datetime(f"{value[:-1]}+00:00")
        if parsed is not None:
            return parsed
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return value
    return value


class ShiftRepository:
    @staticmethod
    def get_shifts():
        try:
            shifts = Shifts.objects.order_by("id").values("id")
            return list(shifts)
        except Exception:
            return APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def get_shifts_by_user_id(user_id):
        try:
            return Shifts.objects.filter(user_id=user_id).order_by("id")
        except Exception:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def get_shifts_by_team_id(team_id):
        try:
            return Shifts.objects.filter(user__team_id=team_id).order_by("id")
        except Exception:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def create_shift(user, start_time, end_time):
        try:
            shift = Shifts.objects.create(
                user=user,
                start_time=_ensure_datetime(start_time),
                end_time=_ensure_datetime(end_time),
            )
            return shift
        except Exception:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def get_shift_by_id(shift_id):
        try:
            return Shifts.objects.get(id=shift_id)
        except Exception:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def update_shift(shift_id, start_time, end_time):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.start_time = _ensure_datetime(start_time)
            shift.end_time = _ensure_datetime(end_time)
            shift.save()
            return shift
        except Exception:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def delete_shift(shift_id):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.delete()
            return True
        except Exception:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def check_in(shift_id, start_time):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.real_start_time = _ensure_datetime(start_time)
            shift.save()
            return shift
        except Shifts.DoesNotExist:
            return {"error": "Shift not found."}
        except Exception as exc:
            return {"error": str(exc)}

    @staticmethod
    def check_out(shift_id, end_time):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.real_end_time = _ensure_datetime(end_time)
            shift.save()
            return shift
        except Shifts.DoesNotExist:
            return {"error": "Shift not found."}
        except Exception as exc:
            return {"error": str(exc)}

    @staticmethod
    def list_shifts_by_user_id_and_date(user_id: str, start: datetime, end: datetime):
        try:
            return Shifts.objects.filter(
                user_id=user_id,
                start_time__lt=end,
                end_time__gt=start,
            ).order_by("start_time")
        except Exception:
            return APIException({"error": "internal server error.", "status_code": 500})
