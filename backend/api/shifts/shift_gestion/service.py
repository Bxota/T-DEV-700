from db_manager.repositories.shift_template_repository import ShiftTemplateRepository
from db_manager.repositories.shift_rule_repository import ShiftRuleRepository
from db_manager.repositories.shift_exception_repository import ShiftExceptionRepository

from ..service import AbstractManager

class ShiftTemplateManager(AbstractManager):
    @staticmethod
    def get_shift_template_by_team_id(team_id: str, active_only: bool):
        return ShiftTemplateRepository.list_by_team(team_id, active_only=active_only)
    
    @staticmethod
    def get_shift_template_by_id(template_id: str):
        return ShiftTemplateRepository.get_by_id(template_id)
    
    @staticmethod
    def create_template(name: str, team_id: str, user_id: str, default_duration_minutes, role_id: str, timezone: str = "Europe/Paris", is_active: bool = True):
        return ShiftTemplateRepository.create_template(
            name=name,
            team_id=team_id,
            created_by_id=user_id,
            default_duration_minutes=default_duration_minutes,
            timezone=timezone,
            role_id=role_id,
            is_active=is_active,
        )
        
    @staticmethod
    def update_template(template_id: str, name: str, default_duration_minutes, timezone, role_id: str, is_active: bool = True):
        return ShiftTemplateRepository.update_template(
            template_id, 
            name=name, 
            default_duration_minutes=default_duration_minutes, 
            timezone=timezone, 
            role_id=role_id,
            is_active=is_active,
        )
        
    @staticmethod
    def delete_template(template_id: str):
        return ShiftTemplateRepository.delete_template(template_id=template_id)

class ShiftRuleManager(AbstractManager):
    @staticmethod
    def get_shift_rule_by_template_id(template_id: str):
        return ShiftRuleRepository.list_by_template(template_id)
    
    @staticmethod
    def get_shift_rule_by_id(rule_id: str):
        return ShiftRuleRepository.get_by_id(rule_id)
    
    @staticmethod
    def update_rule(rule_id: str, apply_to_whole_team: bool):
        return ShiftRuleRepository.update_rule(rule_id=rule_id, apply_to_whole_team=apply_to_whole_team)
    
    @staticmethod
    def clear_assigned_users(rule_id: str):
        return ShiftRuleRepository.clear_assigned_users(rule_id)
    
    @staticmethod
    def assign_users(rule_id: str, user_ids):
        return ShiftRuleRepository.assign_users(rule_id, user_ids)

class ShiftExceptionManager(AbstractManager):
    @staticmethod
    def get_shift_exception_by_rule_id(rule_id: str):
        return ShiftExceptionRepository.list_by_rule(rule_id)
    
    @staticmethod
    def create_exception(rule_id: str, date, override_start_local_time, override_duration_minutes, is_skipped: bool = False, note: str = ""):
        return ShiftExceptionRepository.create_exception(
            rule_id=rule_id,
            date_value=date,
            is_skipped=is_skipped,
            override_start_local_time=override_start_local_time,
            override_duration_minutes=override_duration_minutes,
            note=note,
        )
    
    @staticmethod
    def update_exception(exception_id: str, date, override_start_local_time, override_duration_minutes, is_skipped: bool = False, note: str = ""):
        return ShiftExceptionRepository.update_exception(
            exception_id=exception_id,
            date=date,
            override_start_local_time=override_start_local_time,
            override_duration_minutes=override_duration_minutes,
            is_skipped=is_skipped,
            note=note,
        )
        
    @staticmethod
    def delete_exception(exception_id: str):
        return ShiftExceptionRepository.delete_exception(exception_id=exception_id)