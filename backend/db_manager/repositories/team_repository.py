from db_manager.models import Teams

class TeamRepository:
    @staticmethod
    def get_teams():
        try:
            teams = Teams.objects.order_by('id').values('id', 'name')
            return list(teams)
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_team(name):
        try:
            if Teams.objects.filter(name=name).exists():
                return {"error": "Team with this name already exists."}
            team = Teams.objects.create(name=name)
            return team
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_team_by_id(team_id):
        try:
            return Teams.objects.get(id=team_id)
        except Teams.DoesNotExist:
            return {"error": "Team not found."}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def update_team(team_id, name):
        try:
            team = Teams.objects.get(id=team_id)
            team.name = name
            team.save()
            return team
        except Teams.DoesNotExist:
            return {"error": "Team not found."}
        except Exception as e:
            return {"error": str(e)}
        
    @staticmethod
    def delete_team(team_id):
        try:
            team = Teams.objects.get(id=team_id)
            team.delete()
            return True
        except Teams.DoesNotExist:
            return {"error": "Team not found."}
        except Exception as e:
            return {"error": str(e)}
    