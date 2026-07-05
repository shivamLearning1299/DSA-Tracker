from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Problem, Sheet, SheetProblem, Topic, UserProblemStatus

User = get_user_model()


class ModelTests(APITestCase):
    def test_topic_str(self):
        topic = Topic.objects.create(name="Arrays")
        self.assertEqual(str(topic), "Arrays")

    def test_problem_str(self):
        problem = Problem.objects.create(title="Two Sum", difficulty=Problem.Difficulty.EASY)
        self.assertEqual(str(problem), "Two Sum")

    def test_user_problem_status_unique_together(self):
        user = User.objects.create_user(username="a@example.com", email="a@example.com")
        problem = Problem.objects.create(title="Two Sum", difficulty=Problem.Difficulty.EASY)
        UserProblemStatus.objects.create(user=user, problem=problem)
        with self.assertRaises(Exception):
            UserProblemStatus.objects.create(user=user, problem=problem)


class ProblemApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="a@example.com", email="a@example.com")
        self.other_user = User.objects.create_user(username="b@example.com", email="b@example.com")
        self.topic = Topic.objects.create(name="Arrays")
        self.problem = Problem.objects.create(
            title="Two Sum", difficulty=Problem.Difficulty.EASY
        )
        self.problem.topics.add(self.topic)

    def test_list_requires_authentication(self):
        response = self.client.get("/api/problems/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/problems/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Two Sum")

    def test_problem_status_defaults_to_todo(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/problems/")
        self.assertEqual(response.data[0]["status"], UserProblemStatus.Status.TODO)

    def test_set_status_creates_user_problem_status(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/problems/{self.problem.id}/status/",
            {"status": UserProblemStatus.Status.SOLVED, "notes": "easy one"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], UserProblemStatus.Status.SOLVED)
        status_obj = UserProblemStatus.objects.get(user=self.user, problem=self.problem)
        self.assertEqual(status_obj.notes, "easy one")

    def test_set_status_updates_existing_status(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(
            f"/api/problems/{self.problem.id}/status/",
            {"status": UserProblemStatus.Status.ATTEMPTED},
        )
        self.client.post(
            f"/api/problems/{self.problem.id}/status/",
            {"status": UserProblemStatus.Status.SOLVED},
        )
        self.assertEqual(
            UserProblemStatus.objects.filter(user=self.user, problem=self.problem).count(), 1
        )
        status_obj = UserProblemStatus.objects.get(user=self.user, problem=self.problem)
        self.assertEqual(status_obj.status, UserProblemStatus.Status.SOLVED)

    def test_status_is_per_user(self):
        UserProblemStatus.objects.create(
            user=self.other_user, problem=self.problem, status=UserProblemStatus.Status.SOLVED
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/problems/")
        self.assertEqual(response.data[0]["status"], UserProblemStatus.Status.TODO)

    def test_filter_by_difficulty(self):
        Problem.objects.create(title="Hard One", difficulty=Problem.Difficulty.HARD)
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/problems/", {"difficulty": "hard"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Hard One")


class SheetApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="a@example.com", email="a@example.com")
        self.other_user = User.objects.create_user(username="b@example.com", email="b@example.com")
        self.problem = Problem.objects.create(
            title="Two Sum", difficulty=Problem.Difficulty.EASY
        )

    def test_sheet_list_shows_own_and_public_sheets(self):
        own_sheet = Sheet.objects.create(name="Mine", owner=self.user)
        Sheet.objects.create(name="Private", owner=self.other_user, is_public=False)
        public_sheet = Sheet.objects.create(name="Public", owner=self.other_user, is_public=True)

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/sheets/")
        names = {sheet["name"] for sheet in response.data}
        self.assertEqual(names, {"Mine", "Public"})

    def test_create_sheet_sets_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/sheets/", {"name": "New Sheet"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sheet = Sheet.objects.get(id=response.data["id"])
        self.assertEqual(sheet.owner, self.user)

    def test_add_problem_to_sheet(self):
        sheet = Sheet.objects.create(name="Mine", owner=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/sheets/{sheet.id}/problems/",
            {"problem_id": self.problem.id, "order": 1},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            SheetProblem.objects.filter(sheet=sheet, problem=self.problem).exists()
        )


class StatsApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="a@example.com", email="a@example.com")
        self.topic = Topic.objects.create(name="Arrays")
        self.solved = Problem.objects.create(
            title="Solved One", difficulty=Problem.Difficulty.EASY
        )
        self.solved.topics.add(self.topic)
        self.todo = Problem.objects.create(title="Todo One", difficulty=Problem.Difficulty.MEDIUM)
        UserProblemStatus.objects.create(
            user=self.user, problem=self.solved, status=UserProblemStatus.Status.SOLVED
        )
        UserProblemStatus.objects.create(
            user=self.user, problem=self.todo, status=UserProblemStatus.Status.TODO
        )

    def test_stats_requires_authentication(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_totals(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_solved"], 1)
        self.assertEqual(response.data["by_status"]["solved"], 1)
        self.assertEqual(response.data["by_status"]["todo"], 1)
