from rest_framework.exceptions import ValidationError

class AbstractManager:
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