# tests/repositories/test_user_repository.py

from django.test import TestCase
from db_manager.models import Users, Teams
from db_manager.repositories.user_repository import UserRepository


class UserRepositoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Évite de recréer à chaque test
        cls.team_a = Teams.objects.create(name="Team A")
        cls.team_b = Teams.objects.create(name="Team B")

    # ---------- Helpers ----------
    def make_user(self, email="alice@example.com", team=None, first_name="Alice", last_name="Liddell",
                  phone_number=None, role_id=None, password="Secret123!"):
        u = Users(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role_id=role_id,
            team=team,
        )
        # Important : hash du mot de passe via set_password
        u.set_password(password)
        u.save()
        return u

    # ---------- get_users_by_team_id ----------
    def test_get_users_by_team_id_returns_ordered_value_list(self):
        u1 = self.make_user(email="a@example.com", team=self.team_a, first_name="A")
        u2 = self.make_user(email="b@example.com", team=self.team_a, first_name="B")
        # Un user d'une autre team ne doit pas remonter
        self.make_user(email="c@example.com", team=self.team_b, first_name="C")

        res = UserRepository.get_users_by_team_id(self.team_a.id)

        # Doit être une liste de dicts, triée par id (u1 avant u2)
        self.assertIsInstance(res, list)
        self.assertEqual([row["id"] for row in res], [u1.id, u2.id])
        for row in res:
            self.assertSetEqual(
                set(row.keys()),
                {"id", "email", "first_name", "last_name", "team_id", "phone_number", "role_id"},
            )

    def test_get_users_by_team_id_team_not_found(self):
        res = UserRepository.get_users_by_team_id(team_id=9999)
        self.assertEqual(res, {"error": "Team not found"})

    # ---------- add_user_to_team ----------
    def test_add_user_to_team_success(self):
        user = self.make_user(email="move@example.com", team=self.team_a)
        res = UserRepository.add_user_to_team(user_id=user.id, team_id=self.team_b.id)

        # La méthode renvoie l'instance Users (pas un dict)
        self.assertIsInstance(res, Users)
        user.refresh_from_db()
        self.assertEqual(user.team_id, self.team_b.id)

    def test_add_user_to_team_team_not_found(self):
        user = self.make_user(email="no-team@example.com", team=self.team_a)
        res = UserRepository.add_user_to_team(user_id=user.id, team_id=424242)
        self.assertEqual(res, {"error": "Team not found"})

    def test_add_user_to_team_user_not_found(self):
        res = UserRepository.add_user_to_team(user_id=9999, team_id=self.team_a.id)
        self.assertEqual(res, {"error": "User not found"})

    # ---------- create_user ----------
    def test_create_user_success(self):
        payload = {
            "email": "new@example.com",
            "password": "S3cretPwd!",
            "first_name": "New",
            "last_name": "User",
            "team_id": self.team_a.id,
            "phone_number": "0600000000",
            "role_id": None,
        }
        res = UserRepository.create_user(**payload)

        # Retour attendu : dict (value()s du user), pas l'instance
        self.assertIsInstance(res, dict)
        self.assertEqual(res["email"], payload["email"])
        self.assertEqual(res["first_name"], payload["first_name"])
        self.assertEqual(res["last_name"], payload["last_name"])
        self.assertEqual(res["team_id"], payload["team_id"])
        self.assertEqual(res["phone_number"], payload["phone_number"])
        self.assertIsNone(res["role_id"])

        # Et le password est bien hashé en BDD
        created = Users.objects.get(id=res["id"])
        self.assertTrue(created.check_password(payload["password"]))

    def test_create_user_duplicate_email(self):
        self.make_user(email="dup@example.com")
        res = UserRepository.create_user(
            email="dup@example.com", password="X", first_name="A", last_name="B"
        )
        self.assertEqual(res, {"error": "Email already exists"})

    # ---------- get_user_by_id ----------
    def test_get_user_by_id_found(self):
        user = self.make_user(email="getid@example.com", team=self.team_b, first_name="John", last_name="Doe")
        res = UserRepository.get_user_by_id(user.id)

        self.assertEqual(res["id"], user.id)
        self.assertEqual(res["email"], user.email)
        self.assertEqual(res["team_id"], self.team_b.id)
        self.assertSetEqual(
            set(res.keys()),
            {"id", "email", "first_name", "last_name", "team_id", "phone_number", "role_id"},
        )

    def test_get_user_by_id_not_found(self):
        res = UserRepository.get_user_by_id(9999)
        self.assertEqual(res, {"error": "User not found"})

    # ---------- update_user ----------
    def test_update_user_updates_fields(self):
        user = self.make_user(email="upd@example.com", first_name="Old", last_name="Name", team=self.team_a)
        res = UserRepository.update_user(
            user_id=user.id,
            first_name="NewFirst",
            last_name="NewLast",
            phone_number="0611223344",
        )

        self.assertEqual(res["first_name"], "NewFirst")
        self.assertEqual(res["last_name"], "NewLast")
        self.assertEqual(res["phone_number"], "0611223344")

        user.refresh_from_db()
        self.assertEqual(user.first_name, "NewFirst")
        self.assertEqual(user.last_name, "NewLast")
        self.assertEqual(user.phone_number, "0611223344")

    def test_update_user_password_hashes(self):
        user = self.make_user(email="pwd@example.com", password="OldPwd1!")
        res = UserRepository.update_user(user_id=user.id, password="NewPwd2!")
        self.assertEqual(res["email"], "pwd@example.com")

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPwd2!"))

    def test_update_user_invalid_field(self):
        user = self.make_user(email="badfield@example.com")
        res = UserRepository.update_user(user_id=user.id, not_a_real_field="x")
        self.assertEqual(res, {"error": "Invalid field: not_a_real_field"})

    def test_update_user_not_found(self):
        res = UserRepository.update_user(user_id=9999, first_name="X")
        self.assertEqual(res, {"error": "User not found"})

    # ---------- get_all_users ----------
    def test_get_all_users_returns_value_list(self):
        u1 = self.make_user(email="all1@example.com")
        u2 = self.make_user(email="all2@example.com")
        res = UserRepository.get_all_users()

        self.assertIsInstance(res, list)
        self.assertEqual([row["id"] for row in res], [u1.id, u2.id])
        for row in res:
            self.assertSetEqual(
                set(row.keys()),
                {"id", "email", "first_name", "last_name", "team_id", "phone_number", "role_id"},
            )

    # ---------- delete_user ----------
    def test_delete_user_success(self):
        user = self.make_user(email="del@example.com")
        res = UserRepository.delete_user(user.id)
        self.assertTrue(res)
        self.assertFalse(Users.objects.filter(id=user.id).exists())

    def test_delete_user_not_found(self):
        res = UserRepository.delete_user(9999)
        self.assertEqual(res, {"error": "User not found"})