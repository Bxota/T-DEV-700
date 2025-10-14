from db_manager.repositories.shifts_repository import ShiftRepository
from rest_framework.exceptions import ValidationError
from django.db.models.query import QuerySet

class AbstractManager:
    def check_db_return(element, serializer):
        if isinstance(element, dict) and "error" in element:
            raise ValidationError(element)
        
        if isinstance(element, QuerySet):
            return serializer(element, many=True).data
        else:
            return serializer(element).data
    
    def check_body_element(request, name: str):
        element = request.data.get(name)
        if not element:
            raise ValidationError({"error": f"{name} field is required."})
        
        return element
        
    def check_db_element_exist(className, id: int):
        try:
            element = className.objects.get(pk=id)
            return element
        except className.DoesNotExist:
            raise ValidationError({"error": f"{className.__name__.lower()} not found."})
        
    def check_is_equal(first_element_name, first_element, second_element_name, second_element):
        if first_element != second_element:
            raise ValidationError({"error": f"{first_element_name.__class__.__name__.lower()} and {second_element_name.__class__.__name__.lower()} are not linked."})
        
    def check_is_not_have_element(obj, attr_name: str):
        value = getattr(obj, attr_name, None)
        if value is not None:
            raise ValidationError({
                "error": f"{obj.__class__.__name__.lower()} already has a {attr_name} element"
            })
        
    def check_is_have_element(obj, attr_name: str):
        value = getattr(obj, attr_name, None)
        if value is None:
            raise ValidationError({
                "error": f"{obj.__class__.__name__.lower()} doesn't has a {attr_name} element"
            })
    def check_if_db_element_with_name_exist(className, name: str):
        if className.objects.filter(name=name).exists():
            raise ValidationError({"error": f"{className.__name__.lower()} with this name already exists."})
        
    def check_if_db_element_with_email_exist(className, email: str):
        if className.objects.filter(email=email).exists():
            raise ValidationError({"error": f"{className.__name__.lower()} with this email already exists."})
        
    def check_valid_field_in_kwargs(className, **kwargs):
        valid_fields = ['email', 'first_name', 'last_name', 'team_id', 'phone_number', 'role_id', 'password']
        for key in kwargs.keys():
            if key not in valid_fields:
                raise ValidationError({"error": f"{key} is not a valid field of {className.__name__.lower()}."})
            
    def check_valid_shift_interval(start_time, end_time, user_id):
        if start_time >= end_time:
            raise ValidationError({"error": "start_time must be before end_time."})
            
        for shift in ShiftRepository.get_shifts_by_user_id(user_id):
            if (start_time < shift.end_time and end_time > shift.start_time):
                raise ValidationError({"error": "Shift time interval overlaps with an existing shift."})
            
    def check_is_user_shift(shift_id, user_id):
        if not ShiftRepository.get_shift_by_id(shift_id).user.id == user_id:
            raise ValidationError({"error": "This shift does not belong to this user."})

