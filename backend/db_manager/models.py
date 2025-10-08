from django.db import models

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

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    team = models.ForeignKey(Teams, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "users"

class Shifts(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    real_start_time = models.DateTimeField(blank=True, null=True)
    real_end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "shifts"