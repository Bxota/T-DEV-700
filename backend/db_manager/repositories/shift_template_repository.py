# db_manager/repositories/shift_template_repository.py
from typing import Optional, Iterable, Union
from django.db import IntegrityError, transaction
from db_manager.models import ShiftTemplate, Teams, Roles, Users
from rest_framework.exceptions import APIException


class ShiftTemplateRepository:
    @staticmethod
    def create_template(
        *,
        name: str,
        team_id: int,
        created_by_id: int,
        default_duration_minutes: int,
        timezone: str = "Europe/Paris",
        role_id: Optional[int] = None,
        is_active: bool = True,
    ) -> Union[ShiftTemplate, dict]:
        try:
            team = Teams.objects.filter(id=team_id).first()
            if not team:
                return {"error": "Team not found"}

            created_by = Users.objects.filter(id=created_by_id).first()
            if not created_by:
                return {"error": "Creator user not found"}

            role = None
            if role_id is not None:
                role = Roles.objects.filter(id=role_id).first()
                if not role:
                    return {"error": "Role not found"}

            with transaction.atomic():
                tpl = ShiftTemplate.objects.create(
                    name=name,
                    team=team,
                    created_by=created_by,
                    role=role,
                    default_duration_minutes=default_duration_minutes,
                    timezone=timezone,
                    is_active=is_active,
                )
                return tpl
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def get_by_id(template_id: int) -> Union[ShiftTemplate, dict]:
        try:
            tpl = ShiftTemplate.objects.filter(id=template_id).first()
            if not tpl:
                return {"error": "ShiftTemplate not found"}
            return tpl
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def list_by_team(team_id: int, *, active_only: bool = False):
        qs = ShiftTemplate.objects.filter(team_id=team_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return qs

    @staticmethod
    def update_template(
        template_id: int,
        **fields,
    ) -> Union[ShiftTemplate, dict]:
        try:
            tpl = ShiftTemplate.objects.filter(id=template_id).first()
            if not tpl:
                return {"error": "ShiftTemplate not found"}

            allowed = {
                "name",
                "default_duration_minutes",
                "timezone",
                "is_active",
                "role",
                "role_id",
            }
            for k, v in fields.items():
                if k not in allowed:
                    continue
                if k == "role_id":
                    if v is None:
                        tpl.role = None
                    else:
                        role = Roles.objects.filter(id=v).first()
                        if not role:
                            return {"error": "Role not found"}
                        tpl.role = role
                else:
                    setattr(tpl, k, v)

            tpl.save()
            return tpl
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def set_active(template_id: int, is_active: bool) -> Union[ShiftTemplate, dict]:
        return ShiftTemplateRepository.update_template(template_id, is_active=is_active)

    @staticmethod
    def delete_template(template_id: int) -> Union[dict, None]:
        try:
            tpl = ShiftTemplate.objects.filter(id=template_id).first()
            if not tpl:
                return {"error": "ShiftTemplate not found"}
            tpl.delete()
            return None
        except IntegrityError as e:
            return {"error": str(e)}
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})