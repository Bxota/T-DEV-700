# api/shifts/management/commands/generate_shifts.py
from django.core.management.base import BaseCommand
from datetime import date, timedelta
from api.shifts.generator import generate_occurrences_for_window

class Command(BaseCommand):
    help = "Generate recurring shift occurrences for a rolling window."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=56)  # 8 semaines

    def handle(self, *args, **opts):
        today = date.today()
        res = generate_occurrences_for_window(today, today + timedelta(days=opts["days"]))
        self.stdout.write(self.style.SUCCESS(f"Created {res['created']} shift(s)."))