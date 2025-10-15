# api/shifts/generator.py
from datetime import datetime, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo
from django.db import transaction
from django.utils import timezone
from db_manager.models import ShiftTemplate, ShiftRule, Shifts, Users

def generate_occurrences_for_window(start_date, end_date, team_id=None):
    """
    Matérialise les occurrences dans Shifts pour [start_date, end_date].
    start_date/end_date: objets date ou datetime; on itère par jour.
    """
    rules = (
        ShiftRule.objects
        .select_related("template", "template__team")
        .prefetch_related("assigned_users", "exceptions")
        .filter(template__is_active=True)
    )
    if team_id:
        rules = rules.filter(template__team_id=team_id)

    created = 0
    with transaction.atomic():
        for rule in rules:
            tpl = rule.template
            tz = ZoneInfo(tpl.timezone)

            cur = start_date
            while cur <= end_date:
                cur_date = cur if hasattr(cur, "year") and not isinstance(cur, datetime) else cur.date()

                # 1) bon jour ?
                if cur_date.weekday() != rule.weekday:
                    cur += timedelta(days=1)
                    continue

                # 2) fenêtre d’effet
                if cur_date < rule.effective_from or (rule.effective_to and cur_date > rule.effective_to):
                    cur += timedelta(days=1)
                    continue

                # 3) exception éventuelle
                exc = next((e for e in rule.exceptions.all() if e.date == cur_date), None)
                if exc and exc.is_skipped:
                    cur += timedelta(days=1)
                    continue

                # 4) horaires
                start_local_time = (exc.override_start_local_time if exc else None) or rule.start_local_time
                duration_minutes = (exc.override_duration_minutes if exc else None) or rule.duration_minutes or tpl.default_duration_minutes

                # 5) utilisateurs ciblés
                if rule.apply_to_whole_team:
                    target_users = list(Users.objects.filter(team=tpl.team, is_active=True).only("id"))
                else:
                    target_users = list(rule.assigned_users.all())
                    if not target_users:
                        cur += timedelta(days=1)
                        continue

                # 6) datetimes local → UTC
                start_local_dt = datetime.combine(cur_date, start_local_time).replace(tzinfo=tz)
                end_local_dt = start_local_dt + timedelta(minutes=duration_minutes)
                start_utc = start_local_dt.astimezone(dt_timezone.utc)
                end_utc = end_local_dt.astimezone(dt_timezone.utc)

                # 7) création si non existant
                for u in target_users:
                    exists = Shifts.objects.filter(user=u, start_time=start_utc, end_time=end_utc).exists()
                    if not exists:
                        Shifts.objects.create(
                            user=u,
                            start_time=start_utc,
                            end_time=end_utc,
                            template=tpl,
                            rule=rule,
                        )
                        created += 1

                cur += timedelta(days=1)

    return {"created": created}