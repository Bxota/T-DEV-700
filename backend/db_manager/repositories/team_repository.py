from db_manager.models import Teams

class TeamRepository:
    @staticmethod
    def get_teams():
        return list(Teams.objects.values_list('name', flat=True))
    
    @staticmethod
    def create_team(name):
        team = Teams(name=name)
        team.save()
        return team
    
    @staticmethod
    def get_team_by_id(team_id):
        try:
            return Teams.objects.get(id=team_id)
        except Teams.DoesNotExist:
            return None
        
    @staticmethod
    def update_team(team_id, name):
        team = TeamRepository.get_team_by_id(team_id)
        if team:
            team.name = name
            team.save()
            return team
        return None
        
    @staticmethod
    def delete_team(team_id):
        team = TeamRepository.get_team_by_id(team_id)
        if team:
            team.delete()
            return True
        return False
    