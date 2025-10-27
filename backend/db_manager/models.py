from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # flags obligatoires pour l’admin
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email, password, **extra_fields)

        # Assigner le rôle 'manager' automatiquement
        try:
            from db_manager.models import Roles
            manager_role, _ = Roles.objects.get(name="Manager")
            if hasattr(user, "role"):
                user.role = manager_role
                user.save(update_fields=["role"])
            elif hasattr(user, "roles"):
                user.roles.add(manager_role)
        except Exception:
            # ne bloque pas la création (ex: migrations initiales)
            pass

        return user

class Teams(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "teams"

class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "roles"

class Users(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100,)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    team = models.ForeignKey(Teams, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)

    # champs requis pour Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

class ShiftTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_shift_templates")
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name="shift_templates")  # scope d’équipe
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True, blank=True)  # optionnel: cible un rôle
    default_duration_minutes = models.PositiveIntegerField()  # ex: 480 pour 8h
    timezone = models.CharField(max_length=64, default="Europe/Paris")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "shift_templates"
        unique_together = [("team", "name")]  # pratique pour éviter les doublons dans une équipe

    def __str__(self):
        return f"{self.team.name} · {self.name}"
    
class ShiftRule(models.Model):
    id = models.AutoField(primary_key=True)
    template = models.ForeignKey(ShiftTemplate, on_delete=models.CASCADE, related_name="rules")

    # Récurrence hebdo
    weekday = models.PositiveSmallIntegerField()  # 0=Mon ... 6=Sun (comme Python)
    start_local_time = models.TimeField()         # heure locale (timezone du template)
    duration_minutes = models.PositiveIntegerField()  # override sur la durée par défaut si voulu

    # Fenêtre d'applicabilité
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)  # si vide = indéfini

    # Ciblage
    assigned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="shift_rules")  
    apply_to_whole_team = models.BooleanField(default=False)

    class Meta:
        db_table = "shift_rules"
        indexes = [
            models.Index(fields=["weekday", "effective_from", "effective_to"]),
        ]
        
class ShiftException(models.Model):
    id = models.AutoField(primary_key=True)
    rule = models.ForeignKey(ShiftRule, on_delete=models.CASCADE, related_name="exceptions")
    date = models.DateField()  # dans la timezone du template
    is_skipped = models.BooleanField(default=False)
    override_start_local_time = models.TimeField(null=True, blank=True)
    override_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "shift_exceptions"
        unique_together = [("rule", "date")]

class Shifts(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shifts")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    real_start_time = models.DateTimeField(blank=True, null=True)
    real_end_time = models.DateTimeField(blank=True, null=True)

    # Nouveaux champs (traçabilité)
    template = models.ForeignKey(ShiftTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="occurrences")
    rule = models.ForeignKey(ShiftRule, on_delete=models.SET_NULL, null=True, blank=True, related_name="occurrences")

    class Meta:
        db_table = "shifts"
        indexes = [
            models.Index(fields=["user", "start_time"]),
        ]
