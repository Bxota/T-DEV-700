from db_manager.models import Users

class UserRepository:
    @staticmethod
    def get_users_by_team_id(team_id):
        return Users.objects.filter(team_id=team_id)
    
    @staticmethod
    def create_user(email, first_name, last_name, team_id=None, phone_number=None, role_id=None):
        user = Users(email=email, first_name=first_name, last_name=last_name, team_id=team_id, phone_number=phone_number, role_id=role_id)
        user.save()
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        try:
            return Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return None

    @staticmethod
    def update_team_by_user_id(user_id, team_id):
        user = UserRepository.get_user_by_id(user_id)
        if user:
            user.team_id = team_id
            user.save()
            return user
        return None
