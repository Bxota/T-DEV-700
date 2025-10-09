import pytest
from django.db import IntegrityError
from django.utils import timezone

from db_manager.models import Users, Teams, Roles, Shifts


@pytest.mark.django_db
class TestTeamsModel:
    def test_create_team_and_db_table(self):
        t = Teams.objects.create(name="Backend")
        assert t.id is not None
        assert t.name == "Backend"
        # db_table
        assert Teams._meta.db_table == "teams"

    def test_team_name_unique(self):
        Teams.objects.create(name="Backend")
        with pytest.raises(IntegrityError):
            Teams.objects.create(name="Backend")


@pytest.mark.django_db
class TestRolesModel:
    def test_create_role_and_db_table(self):
        r = Roles.objects.create(name="manager")
        assert r.id is not None
        assert r.name == "manager"
        # db_table
        assert Roles._meta.db_table == "roles"

    def test_role_name_unique(self):
        Roles.objects.create(name="employee")
        with pytest.raises(IntegrityError):
            Roles.objects.create(name="employee")


@pytest.mark.django_db
class TestUsersModel:
    def test_user_manager_create_user_requires_email(self):
        with pytest.raises(ValueError):
            Users.objects.create_user(email=None, password="x")

    def test_user_manager_create_user_hashes_password_and_normalizes_email(self):
        user = Users.objects.create_user(email="John.Doe@Example.COM", password="secret123")
        assert user.id is not None
        assert user.check_password("secret123") is True
        # Domaine en minuscules
        assert user.email.endswith("@example.com")
        # __str__
        assert str(user) == user.email
        # db_table
        assert Users._meta.db_table == "users"

    def test_user_email_unique(self):
        Users.objects.create_user(email="a@example.com", password="x")
        with pytest.raises(IntegrityError):
            Users.objects.create_user(email="a@example.com", password="y")

    def test_create_superuser_flags(self):
        su = Users.objects.create_superuser(email="admin@example.com", password="adminpw")
        assert su.is_superuser is True
        assert su.is_staff is True
        assert su.check_password("adminpw") is True

    def test_phone_number_optional(self):
        user = Users.objects.create_user(email="u1@example.com", password="x", phone_number=None)
        assert user.phone_number is None
        user2 = Users.objects.create_user(email="u2@example.com", password="x", phone_number="0612345678")
        assert user2.phone_number == "0612345678"

    def test_team_and_role_nullable_and_set_null_on_delete(self):
        team = Teams.objects.create(name="Backend")
        role = Roles.objects.create(name="manager")
        user = Users.objects.create_user(email="u@example.com", password="x", team=team, role=role)

        assert user.team_id == team.id
        assert user.role_id == role.id

        # Delete team/role -> Users.team/role passent à NULL (SET_NULL)
        team.delete()
        role.delete()
        user.refresh_from_db()
        assert user.team is None
        assert user.role is None


@pytest.mark.django_db
class TestShiftsModel:
    def test_create_shift_and_related_name(self):
        user = Users.objects.create_user(email="shiftuser@example.com", password="x")
        start = timezone.now()
        end = start + timezone.timedelta(hours=2)

        s = Shifts.objects.create(user=user, start_time=start, end_time=end)
        assert s.id is not None
        assert s.user == user
        assert s.start_time == start
        assert s.end_time == end
        # related_name "shifts"
        assert list(user.shifts.all()) == [s]
        # db_table
        assert Shifts._meta.db_table == "shifts"

    def test_shift_optional_real_times(self):
        user = Users.objects.create_user(email="opt@example.com", password="x")
        start = timezone.now()
        end = start + timezone.timedelta(hours=1)
        s = Shifts.objects.create(
            user=user, start_time=start, end_time=end,
            real_start_time=None, real_end_time=None
        )
        assert s.real_start_time is None
        assert s.real_end_time is None

    def test_delete_user_cascades_on_shifts(self):
        user = Users.objects.create_user(email="casc@example.com", password="x")
        start = timezone.now()
        end = start + timezone.timedelta(hours=1)
        Shifts.objects.create(user=user, start_time=start, end_time=end)

        # Vérifie bien qu'on a un shift
        assert Shifts.objects.count() == 1

        # CASCADE sur user -> supprime les shifts
        user.delete()
        assert Shifts.objects.count() == 0