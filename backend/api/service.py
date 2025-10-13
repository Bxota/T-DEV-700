from rest_framework.exceptions import ValidationError

class AbstractManager:
    def check_db_return(element, serializer):
        if isinstance(element, dict) and "error" in element:
            raise ValidationError(element)
        
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