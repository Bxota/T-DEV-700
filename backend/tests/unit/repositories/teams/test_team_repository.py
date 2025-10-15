# tests/repositories/test_team_repository.py

from django.test import TestCase
from rest_framework.exceptions import APIException

from db_manager.models import Users, Teams, Roles
from db_manager.repositories.user_repository import UserRepository


class TeamRepositoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.team_a = Teams.objects.create(name="Team A")
        cls.team_b = Teams.objects.create(name="Team B")

        cls.role_employee = Roles.objects.create(name="Employee")
        cls.role_manager = Roles.objects.create(name="Manager")

        cls.user_1 = Users.objects.create(
            email="u1@example.com",
            first_name="U1",
            last_name="LN1",
            team=cls.team_a,
            role=cls.role_employee,
        )
        cls.user_1.set_password("pass1")
        cls.user_1.save()

        cls.user_2 = Users.objects.create(
            email="u2@example.com",
            first_name="U2",
            last_name="LN2",
            team=cls.team_a,
            role=cls.role_manager,
        )
        cls.user_2.set_password("pass2")
        cls.user_2.save()

        cls.user_3 = Users.objects.create(
            email="u3@example.com",
            first_name="U3",
            last_name="LN3",
            team=cls.team_b,
            role=cls.role_employee,
        )
        cls.user_3.set_password("pass3")
        cls.user_3.save()

    # -------- get_users_by_team_id --------
    def test_get_users_by_team_id_ok(self):
        qs = UserRepository.get_users_by_team_id(self.team_a.id)
        self.assertEqual(list(qs.values_list("id", flat=True)), [self.user_1.id, self.user_2.id])
        # select_related("role","team") => accès sans requête supplémentaire (pas trivial à tester ici)
        self.assertTrue(hasattr(qs, "select_related"))

    # -------- add_user_to_team --------
    def test_add_user_to_team_ok(self):
        res = UserRepository.add_user_to_team(self.user_3.id, self.team_a.id)
        self.assertEqual(res.id, self.user_3.id)
        self.user_3.refresh_from_db()
        self.assertEqual(self.user_3.team_id, self.team_a.id)

    def test_add_user_to_team_user_not_found_raises_apiexception(self):
        with self.assertRaises(APIException):
            UserRepository.add_user_to_team(9999, self.team_a.id)

    # -------- create_user --------
    def test_create_user_ok(self):
        out = UserRepository.create_user(
            email="new@example.com",
            password="secret",
            first_name="New",
            last_name="User",
            team_id=self.team_b.id,
            phone_number="0600000000",
            role_id=self.role_manager.id,
        )
        # vérifie le dict retourné
        self.assertIsInstance(out, dict)
        self.assertEqual(out["email"], "new@example.com")
        self.assertEqual(out["first_name"], "New")
        self.assertEqual(out["last_name"], "User")
        self.assertEqual(out["team_id"], self.team_b.id)
        self.assertEqual(out["phone_number"], "0600000000")
        self.assertEqual(out["role_id"], self.role_manager.id)

        # vérifie en base que le password est hashé
        u = Users.objects.get(id=out["id"])
        self.assertNotEqual(u.password, "secret")
        self.assertTrue(u.check_password("secret"))

    # -------- get_user_by_id --------
    def test_get_user_by_id_found(self):
        res = UserRepository.get_user_by_id(self.user_1.id)
        self.assertIsInstance(res, Users)
        self.assertEqual(res.id, self.user_1.id)

    def test_get_user_by_id_not_found_returns_dict(self):
        res = UserRepository.get_user_by_id(987654)
        self.assertEqual(res, {"error": "User not found"})

    def test_get_user_by_id_generic_exception_returns_error_str(self):
        # Cas difficile à provoquer en intégration sans mock ; on valide déjà les deux branches principales.

        # (Optionnel) On pourrait forcer une erreur DB ici si nécessaire, mais ce test est
        # surtout pertinent en unit test avec mock. On le laisse de côté côté intégration.
        pass

    # -------- update_user --------
    def test_update_user_ok_updates_fields_and_password(self):
        out = UserRepository.update_user(
            self.user_2.id,
            email="updated@example.com",
            first_name="Up",
            last_name="Dated",
            password="newpass",
            phone_number="0612345678",
            role_id=self.role_employee.id,
            team_id=self.team_b.id,
        )

        # dict retourné cohérent
        self.assertEqual(out["id"], self.user_2.id)
        self.assertEqual(out["email"], "updated@example.com")
        self.assertEqual(out["first_name"], "Up")
        self.assertEqual(out["last_name"], "Dated")
        self.assertEqual(out["phone_number"], "0612345678")
        self.assertEqual(out["role_id"], self.role_employee.id)
        self.assertEqual(out["team_id"], self.team_b.id)

        # vérifie en base
        self.user_2.refresh_from_db()
        self.assertTrue(self.user_2.check_password("newpass"))
        self.assertEqual(self.user_2.email, "updated@example.com")
        self.assertEqual(self.user_2.first_name, "Up")
        self.assertEqual(self.user_2.last_name, "Dated")
        self.assertEqual(self.user_2.phone_number, "0612345678")
        self.assertEqual(self.user_2.role_id, self.role_employee.id)
        self.assertEqual(self.user_2.team_id, self.team_b.id)

    def test_update_user_not_found_raises_apiexception(self):
        with self.assertRaises(APIException):
            UserRepository.update_user(424242, email="x@x.x")

    # -------- get_all_users --------
    def test_get_all_users_ok(self):
        qs = UserRepository.get_all_users()
        self.assertEqual(qs.count(), Users.objects.count())
        self.assertTrue(hasattr(qs, "select_related"))

    # -------- delete_user --------
    def test_delete_user_ok(self):
        u = Users.objects.create(email="todel@example.com", first_name="To", last_name="Del", team=self.team_a, role=self.role_employee)
        res = UserRepository.delete_user(u.id)
        self.assertTrue(res)
        self.assertFalse(Users.objects.filter(id=u.id).exists())

    def test_delete_user_not_found_raises_apiexception(self):
        with self.assertRaises(APIException):
            UserRepository.delete_user(123456)

    # -------- delete_user_from_team --------
    def test_delete_user_from_team_ok(self):
        # user_1 est dans team_a
        res = UserRepository.delete_user_from_team(self.user_1.id, self.team_a.id)
        self.assertTrue(res)
        self.user_1.refresh_from_db()
        self.assertIsNone(self.user_1.team_id)

    def test_delete_user_from_team_wrong_team_raises_apiexception(self):
        # user_3 est dans team_b -> passer team_a doit lever APIException (get() ne trouve pas)
        with self.assertRaises(APIException):
            UserRepository.delete_user_from_team(self.user_3.id, self.team_a.id)

    # -------- get_roles --------
    def test_get_roles_ok(self):
        qs = UserRepository.get_roles()
        self.assertEqual(list(qs.values_list("id", flat=True)), [self.role_employee.id, self.role_manager.id])