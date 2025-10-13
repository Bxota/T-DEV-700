from db_manager.repositories.shifts_repository import ShiftRepository
from db_manager.models import Users

from rest_framework.exceptions import ValidationError

from datetime import datetime

from ..service import AbstractManager

class ShiftManager(AbstractManager):
    @staticmethod
    def list_shifts():
        return ShiftRepository.get_shifts()
    
    def list_shifts_by_user_id(user_id: int):
        return ShiftRepository.get_shifts_by_user_id(user_id=user_id)

    @staticmethod
    def create_shift(user: Users, start_time: datetime, end_time: datetime):
        return ShiftRepository.create_shift(user=user, start_time=start_time, end_time=end_time)

    @staticmethod
    def get_shift_by_id(shift_id: int):
        return ShiftRepository.get_shift_by_id(shift_id)
    
    @staticmethod
    def update_shift(shift_id: int, start_time: datetime, end_time: datetime):
        return ShiftRepository.update_shift(shift_id=shift_id, start_time=start_time, end_time=end_time)
    
    @staticmethod
    def delete_shift(shift_id: int):
        return ShiftRepository.delete_shift(shift_id)
        
    @staticmethod
    def check_in(shift_id: int, start_time: datetime):
        return ShiftRepository.check_in(shift_id=shift_id, start_time=start_time)
    
    @staticmethod
    def check_out(shift_id: int, end_time: datetime):
        return ShiftRepository.check_out(shift_id=shift_id, end_time=end_time)       