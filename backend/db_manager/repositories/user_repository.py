from db_manager.models import Teams, Users

class UserRepository:        
    @staticmethod
    def get_users_by_team_id(team_id):
        try:
            if not Teams.objects.filter(id=team_id).exists():
                return {"error": "Team not found"}
            return Users.objects.filter(team_id=team_id).order_by('id')
        except Exception as e:
            return {"error": str(e)}
        
    @staticmethod
    def add_user_to_team(user_id, team_id):
        try:
            if not Teams.objects.filter(id=team_id).exists():
                return {"error": "Team not found"}
            user = Users.objects.get(id=user_id)
            user.team_id = team_id
            user.save()
            return user
        except Users.DoesNotExist:
            return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def create_user(email, password, first_name=None, last_name=None, team_id=None, phone_number=None, role_id=None):
        try:
            if Users.objects.filter(email=email).exists():
                return {"error": "Email already exists"}
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
            return {"error": str(e)}
    
    @staticmethod
    def get_user_by_id(user_id):
        try:
            user = Users.objects.filter(id=user_id).values('id', 'email', 'first_name', 'last_name', 'team_id', 'phone_number', 'role_id').first()
            if not user:
                return {"error": "User not found"}
            return user
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def update_user(user_id, **kwargs):
        try:
            valid_fields = ['email', 'first_name', 'last_name', 'team_id', 'phone_number', 'role_id', 'password']
            user = Users.objects.get(id=user_id)
            for key, value in kwargs.items():
                if hasattr(user, key) and key in valid_fields:
                    if key == "password":
                        user.set_password(value)
                    else:
                        setattr(user, key, value)
                else:
                    return {"error": f"Invalid field: {key}"}
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
        except Users.DoesNotExist:
            return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_all_users():
        try:
            return list(Users.objects.all().order_by('id').values('id', 'email', 'first_name', 'last_name', 'team_id', 'phone_number', 'role_id'))
        except Exception as e:
            return {"error": str(e)}
        
    @staticmethod
    def delete_user(user_id):
        try:
            user = Users.objects.get(id=user_id)
            user.delete()
            return True
        except Users.DoesNotExist:
            return {"error": "User not found"}
        except Exception as e:
            return {"error": str(e)}
