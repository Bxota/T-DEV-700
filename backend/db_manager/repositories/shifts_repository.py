from db_manager.models import Shifts
from rest_framework.exceptions import APIException

class ShiftRepository:
    @staticmethod
    def get_shifts():
        try:
            shifts = Shifts.objects.order_by('id').values('id')
            return list(shifts)
        except Exception as e:
            return APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def get_shifts_by_user_id(user_id):
        try:
            return Shifts.objects.filter(user_id=user_id).order_by('id')
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def get_shifts_by_team_id(team_id):
        try:
            return Shifts.objects.filter(user__team_id=team_id).order_by('id')
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def create_shift(user, start_time, end_time):
        try:
            shift = Shifts.objects.create(
                user=user,
                start_time=start_time,
                end_time=end_time,
            )
            return shift
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def get_shift_by_id(shift_id):
        try:
            return Shifts.objects.get(id=shift_id)
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def update_shift(shift_id, start_time, end_time):   
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.start_time = start_time
            shift.end_time = end_time
            shift.save()
            return shift
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def delete_shift(shift_id):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.delete()
            return True
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def check_in(shift_id, start_time):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.real_start_time = start_time
            shift.save()
            return shift
        except Shifts.DoesNotExist:
            return {"error": "Shift not found."}
        except Exception as e:
            return {"error": str(e)}
        
    @staticmethod
    def check_out(shift_id, end_time):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.real_end_time = end_time
            shift.save()
            return shift
        except Shifts.DoesNotExist:
            return {"error": "Shift not found."}
        except Exception as e:
            return {"error": str(e)}   