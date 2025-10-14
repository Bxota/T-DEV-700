from db_manager.repositories.user_repository import UserRepository
from api.service import AbstractManager

class UserManager(AbstractManager):
    @staticmethod
    def get_users_by_team_id(team_id: int):
        return UserRepository.get_users_by_team_id(team_id)
    
    @staticmethod
    def add_user_to_team(user_id: int, team_id: int):
        return UserRepository.add_user_to_team(user_id, team_id)
    
    @staticmethod
    def get_all_users():
        return UserRepository.get_all_users()
    
    @staticmethod
    def get_user_by_id(user_id: int):
        return UserRepository.get_user_by_id(user_id)
    
    @staticmethod
    def update_user(user_id: int, **kwargs):
        return UserRepository.update_user(user_id, **kwargs)
    
    @staticmethod
    def create_user(email: str, password: str, **kwargs):
        return UserRepository.create_user(email, password, **kwargs)
    
    @staticmethod
    def delete_user(user_id: int):
        return UserRepository.delete_user(user_id)
    
    @staticmethod
    def delete_user_from_team(user_id: int, team_id: int):
        return UserRepository.delete_user_from_team(user_id, team_id)
    
    @staticmethod
    def get_roles():
        return UserRepository.get_roles()
