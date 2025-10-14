from db_manager.models import Teams, Users
from rest_framework.exceptions import APIException

class UserRepository:        
    @staticmethod
    def get_users_by_team_id(team_id):
        try:
            return Users.objects.filter(team_id=team_id).order_by('id')
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def add_user_to_team(user_id, team_id):
        try:
            user = Users.objects.get(id=user_id)
            user.team_id = team_id
            user.save()
            return user
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
    
    @staticmethod
    def create_user(email, password, first_name=None, last_name=None, team_id=None, phone_number=None, role_id=None):
        try:
            user = Users(
                email=email,
                first_name=first_name,
                last_name=last_name,
                team_id=team_id,
                phone_number=phone_number,
                role_id=role_id
            )
            user.set_password(password)
            user.save()
            return {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'team_id': user.team_id,
                'phone_number': user.phone_number,
                'role_id': user.role_id
            }
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
    
    @staticmethod
    def get_user_by_id(user_id):
        try:
            user = Users.objects.get(id=user_id)
            return user
        except Users.DoesNotExist:
            return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def update_user(user_id, **kwargs):
        try:
            user = Users.objects.get(id=user_id)
            for key, value in kwargs.items():
                    if key == "password":
                        user.set_password(value)
                    else:
                        setattr(user, key, value)
            user.save()
            return {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'team_id': user.team_id,
                'phone_number': user.phone_number,
                'role_id': user.role_id
            }
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
    
    @staticmethod
    def get_all_users():
        try:
            return list(Users.objects.all().order_by('id').values('id', 'email', 'first_name', 'last_name', 'team_id', 'phone_number', 'role_id'))
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def delete_user(user_id):
        try:
            user = Users.objects.get(id=user_id)
            user.delete()
            return True
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def delete_user_from_team(user_id, team_id):
        try:
            user = Users.objects.get(id=user_id, team_id=team_id)
            user.team_id = None
            user.save()
            return True
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
