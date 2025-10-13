from db_manager.models import Teams
from rest_framework.exceptions import APIException

class TeamRepository:
    @staticmethod
    def get_teams():
        try:
            teams = Teams.objects.order_by('id').values('id', 'name')
            return list(teams)
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def create_team(name):
        try:
            team = Teams.objects.create(name=name)
            return team
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def get_team_by_id(team_id):
        try:
            return Teams.objects.get(id=team_id)
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})

    @staticmethod
    def update_team(team_id, name):
        try:
            team = Teams.objects.get(id=team_id)
            team.name = name
            team.save()
            return team
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
        
    @staticmethod
    def delete_team(team_id):
        try:
            team = Teams.objects.get(id=team_id)
            team.delete()
            return True
        except Exception as e:
            raise APIException({"error": "internal server error.", "status_code": 500})
    