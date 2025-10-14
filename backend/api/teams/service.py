from api.service import AbstractManager
from db_manager.repositories.team_repository import TeamRepository

from django.utils.timezone import now
from datetime import timedelta
from db_manager.models import Shifts    
        
from django.db.models import Count, Q, F, Sum, DurationField, ExpressionWrapper
from django.utils.timezone import now

class TeamManager(AbstractManager):
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
    
    @staticmethod
    def compute_lateness_stats(shifts):
        try:
            total_with_checkin = shifts.exclude(real_start_time__isnull=True).count()
            late_shifts = shifts.filter(real_start_time__gt=F("start_time")).count()

            if total_with_checkin == 0:
                return None, None

            lateness_rate = round((late_shifts / total_with_checkin) * 100, 2)
            return lateness_rate, late_shifts

        except Exception as e:
            print("Erreur dans compute_lateness_stats:", e)
            raise
        
    @staticmethod
    def compute_absences_stats(shifts):
        try:
            now_dt = now()
            totalShifts = shifts.count()
            
            absence_shifts = shifts.filter(
                real_start_time__isnull=True,
                real_end_time__isnull=True,
                end_time__lt=now_dt
            ).count()
            
            if totalShifts == 0:
                return None, None
            
            absences_rate = round((absence_shifts / totalShifts) * 100, 2)
            
            return absences_rate, absence_shifts
            
        except Exception as e:
            print("Erreur dans compute_lateness_stats:", e)
            raise

    @staticmethod
    def compute_total_worked_minutes(shifts):
        user_shifts = shifts.filter(
            real_start_time__isnull=False,
            real_end_time__isnull=False
        )
        
        total_duration = timedelta()

        for shift in user_shifts:
            duration = shift.real_end_time - shift.real_start_time
            total_duration += duration

        return round(total_duration.total_seconds() / 60, 2)
    
    @staticmethod
    def generate_user_kpi_report(user, shifts):
        late_rate, late_count = TeamManager.compute_lateness_stats(shifts)
        absence_rate, absence_count = TeamManager.compute_absences_stats(shifts)
        return {
            "user_id": user.id,
            "lateness_rate": late_rate,
            "lateness_count": late_count,
            "absences_rate": absence_rate,
            "absences_count": absence_count,
            "total_shifts": shifts.count(),
            "total_worked_minutes": TeamManager.compute_total_worked_minutes(shifts),
        }
        

    def generate_team_kpi_report(members_qs, *, start=None, end=None):
        shifts = Shifts.objects.filter(user__in=members_qs)
        if start:
            shifts = shifts.filter(start_time__gte=start)
        if end:
            shifts = shifts.filter(start_time__lt=end)

        agg = shifts.aggregate(
            total_shifts=Count('id'),
            total_with_checkin=Count('id', filter=Q(real_start_time__isnull=False)),
            late_shifts=Count('id', filter=Q(real_start_time__gt=F('start_time'))),
            absence_shifts=Count(
                'id',
                filter=Q(
                    real_start_time__isnull=True,
                    real_end_time__isnull=True,
                    end_time__lt=now()
                )
            ),
            worked_duration=Sum(
                ExpressionWrapper(
                    F('real_end_time') - F('real_start_time'),
                    output_field=DurationField(),
                ),
                filter=Q(real_start_time__isnull=False, real_end_time__isnull=False),
            ),
        )

        total_shifts = agg['total_shifts'] or 0
        total_with_checkin = agg['total_with_checkin'] or 0
        late_shifts = agg['late_shifts'] or 0
        absence_shifts = agg['absence_shifts'] or 0
        worked_duration = agg['worked_duration']

        lateness_rate = round(late_shifts / total_with_checkin * 100, 2) if total_with_checkin else None
        absences_rate = round(absence_shifts / total_shifts * 100, 2) if total_shifts else None
        total_worked_minutes = int(worked_duration.total_seconds() // 60) if worked_duration else 0

        return {
            "members": members_qs.count(),
            "total_shifts": total_shifts,
            "total_with_checkin": total_with_checkin,
            "lateness_count": late_shifts,
            "lateness_rate": lateness_rate,
            "absences_count": absence_shifts,
            "absences_rate": absences_rate,
            "total_worked_minutes": total_worked_minutes
        }