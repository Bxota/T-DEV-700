from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Roles

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    if Roles.objects.count() == 0:
        Roles.objects.bulk_create([
            Roles(name="Manager"),
            Roles(name="Employee"),
        ])