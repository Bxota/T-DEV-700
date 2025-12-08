# db_manager/repositories/shift_exception_repository.py
from typing import Optional, Union
from datetime import date, time as time_type
from django.db import IntegrityError, transaction
from db_manager.models import ShiftException, ShiftRule
from rest_framework.exceptions import APIException


class ShiftExceptionRepository:
    @staticmethod
    def list_all():
        return ShiftException.objects.all().order_by("id")

    @staticmethod
    def create_exception(
        *,
        rule_id: int,
        date_value: date,
        is_skipped: bool = False,
        override_start_local_time: Optional[time_type] = None,
        override_duration_minutes: Optional[int] = None,
        note: str = "",
    ) -> Union[ShiftException, dict]:
        try:
            rule = ShiftRule.objects.filter(id=rule_id).first()
            if not rule:
                return {"error": "ShiftRule not found"}

            with transaction.atomic():
                exc = ShiftException.objects.create(
                    rule=rule,
                    date=date_value,
                    is_skipped=is_skipped,
                    override_start_local_time=override_start_local_time,
                    override_duration_minutes=override_duration_minutes,
                    note=note or "",
                )
                return exc
        except IntegrityError as e:
            # ex: unique_together (rule, date) violée
            return {"error": str(e)}
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def get_by_id(exception_id: int) -> Union[ShiftException, dict]:
        try:
            exc = ShiftException.objects.filter(id=exception_id).first()
            if not exc:
                return {"error": "ShiftException not found"}
            return exc
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def list_by_rule(rule_id: int):
        return ShiftException.objects.filter(rule_id=rule_id).order_by("date")

    @staticmethod
    def update_exception(
        exception_id: int,
        **fields,
    ) -> Union[ShiftException, dict]:
        try:
            exc = ShiftException.objects.filter(id=exception_id).first()
            if not exc:
                return {"error": "ShiftException not found"}

            allowed = {
                "is_skipped",
                "override_start_local_time",
                "override_duration_minutes",
                "note",
                "date",
            }
            for k, v in fields.items():
                if k not in allowed:
                    continue
                setattr(exc, k, v)

            exc.save()
            return exc
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def delete_exception(exception_id: int) -> Union[dict, None]:
        try:
            exc = ShiftException.objects.filter(id=exception_id).first()
            if not exc:
                return {"error": "ShiftException not found"}
            exc.delete()
            return None
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})
