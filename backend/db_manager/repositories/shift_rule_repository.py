# db_manager/repositories/shift_rule_repository.py
from typing import Optional, Iterable, Union
from datetime import date, time as time_type
from django.db import IntegrityError, transaction
from db_manager.models import ShiftRule, ShiftTemplate, Users


class ShiftRuleRepository:
    @staticmethod
    def create_rule(
        *,
        template_id: int,
        weekday: int,                           # 0=Mon ... 6=Sun
        start_local_time: time_type,
        duration_minutes: int,
        effective_from: date,
        effective_to: Optional[date] = None,
        apply_to_whole_team: bool = False,
        assigned_user_ids: Optional[Iterable[int]] = None,
    ) -> Union[ShiftRule, dict]:
        try:
            tpl = ShiftTemplate.objects.filter(id=template_id).first()
            if not tpl:
                return {"error": "ShiftTemplate not found"}

            if not (0 <= weekday <= 6):
                return {"error": "weekday must be in [0..6]"}

            with transaction.atomic():
                rule = ShiftRule.objects.create(
                    template=tpl,
                    weekday=weekday,
                    start_local_time=start_local_time,
                    duration_minutes=duration_minutes,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    apply_to_whole_team=apply_to_whole_team,
                )

                if not apply_to_whole_team and assigned_user_ids:
                    users = list(Users.objects.filter(id__in=assigned_user_ids, is_active=True))
                    if len(users) != len(set(assigned_user_ids)):
                        # au moins un user n’existe pas
                        return {"error": "One or more users not found"}
                    rule.assigned_users.set(users)

                return rule
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_by_id(rule_id: int) -> Union[ShiftRule, dict]:
        try:
            rule = (
                ShiftRule.objects.select_related("template")
                .prefetch_related("assigned_users")
                .filter(id=rule_id)
                .first()
            )
            if not rule:
                return {"error": "ShiftRule not found"}
            return rule
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def list_by_template(template_id: int):
        return (
            ShiftRule.objects.select_related("template")
            .prefetch_related("assigned_users")
            .filter(template_id=template_id)
            .order_by("weekday", "start_local_time")
        )

    @staticmethod
    def update_rule(
        rule_id: int,
        **fields,
    ) -> Union[ShiftRule, dict]:
        try:
            rule = ShiftRule.objects.filter(id=rule_id).first()
            if not rule:
                return {"error": "ShiftRule not found"}

            allowed = {
                "weekday",
                "start_local_time",
                "duration_minutes",
                "effective_from",
                "effective_to",
                "apply_to_whole_team",
            }
            for k, v in fields.items():
                if k not in allowed:
                    continue
                if k == "weekday" and v is not None:
                    if not (0 <= int(v) <= 6):
                        return {"error": "weekday must be in [0..6]"}
                setattr(rule, k, v)

            rule.save()
            return rule
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def assign_users(rule_id: int, user_ids: Iterable[int]) -> Union[ShiftRule, dict]:
        """
        Définit la liste des users assignés (et met apply_to_whole_team=False).
        """
        try:
            rule = ShiftRule.objects.filter(id=rule_id).first()
            if not rule:
                return {"error": "ShiftRule not found"}

            users = list(Users.objects.filter(id__in=user_ids, is_active=True))
            if len(users) != len(set(user_ids)):
                return {"error": "One or more users not found"}

            rule.apply_to_whole_team = False
            rule.save(update_fields=["apply_to_whole_team"])
            rule.assigned_users.set(users)
            return rule
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def clear_assigned_users(rule_id: int) -> Union[ShiftRule, dict]:
        try:
            rule = ShiftRule.objects.filter(id=rule_id).first()
            if not rule:
                return {"error": "ShiftRule not found"}
            rule.assigned_users.clear()
            return rule
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete_rule(rule_id: int) -> Union[dict, None]:
        try:
            rule = ShiftRule.objects.filter(id=rule_id).first()
            if not rule:
                return {"error": "ShiftRule not found"}
            rule.delete()
            return None
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}