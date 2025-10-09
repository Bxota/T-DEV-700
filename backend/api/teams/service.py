from db_manager.repositories.team_repository import TeamRepository

class TeamManager:
    @staticmethod
    def list_teams():
        return TeamRepository.get_teams()

    @staticmethod
    def create_team(name: str):
        return TeamRepository.create_team(name)

    @staticmethod
    def get_team_by_id(team_id: int):
        return TeamRepository.get_team_by_id(team_id)
    
    @staticmethod
    def update_team(team_id: int, name: str):
        return TeamRepository.update_team(team_id, name)
    
    @staticmethod
    def delete_team(team_id: int):
        return TeamRepository.delete_team(team_id)
        