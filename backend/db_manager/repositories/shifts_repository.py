from db_manager.models import Shifts

class ShiftRepository:
    @staticmethod
    def get_shifts():
        try:
            shifts = Shifts.objects.order_by('id').values('id')
            return list(shifts)
        except Exception as e:
            return {"error": str(e)}
        
    @staticmethod
    def get_shifts_by_user_id(user_id):
        try:
            shifts = Shifts.objects.filter(user_id=user_id)
            return list(shifts)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_shift(user, start_time, end_time):
        try:
            if Shifts.objects.filter(
                user=user,
                start_time=start_time,
                end_time=end_time,
            ).exists():
                return {"error": "Shift with this user and start/end time already exists."}

            shift = Shifts.objects.create(
                user=user,
                start_time=start_time,
                end_time=end_time,
            )
            return shift
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_shift_by_id(shift_id):
        try:
            return Shifts.objects.get(id=shift_id)
        except Shifts.DoesNotExist:
            return {"error": "Shift not found."}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def update_shift(shift_id, start_time, end_time):   
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.start_time = start_time
            shift.end_time = end_time
            shift.save()
            return shift
        except Shifts.DoesNotExist:
            return {"error": "Shift not found."}
        except Exception as e:
            return {"error": str(e)}
        
    @staticmethod
    def delete_shift(shift_id):
        try:
            shift = Shifts.objects.get(id=shift_id)
            shift.delete()
            return True
        except Shifts.DoesNotExist:
            return {"error": "Shift not found."}
        except Exception as e:
            return {"error": str(e)}
    