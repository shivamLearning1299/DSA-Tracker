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

    def test_filter_by_source(self):
        Problem.objects.create(
            title="Leet One", difficulty=Problem.Difficulty.EASY, source="leetcode"
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/problems/", {"source": "leetcode"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Leet One")

    def test_create_problem_with_topics(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/problems/",
            {
                "title": "Three Sum",
                "difficulty": Problem.Difficulty.MEDIUM,
                "topic_ids": [self.topic.id],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Problem.objects.get(id=response.data["id"])
        self.assertEqual(list(created.topics.all()), [self.topic])

    def test_create_problem_with_invalid_difficulty_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/problems/",
            {"title": "Bad Problem", "difficulty": "impossible"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Problem.objects.filter(title="Bad Problem").exists())


class TopicApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="a@example.com", email="a@example.com")
        self.topic = Topic.objects.create(name="Arrays")

    def test_list_topics(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/topics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Arrays")

    def test_create_topic(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/topics/", {"name": "Graphs"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Topic.objects.filter(name="Graphs").exists())

    def test_create_duplicate_topic_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/topics/", {"name": "Arrays"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_topic(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f"/api/topics/{self.topic.id}/", {"name": "Sliding Window"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.name, "Sliding Window")

    def test_delete_topic(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/topics/{self.topic.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Topic.objects.filter(id=self.topic.id).exists())


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

    def test_add_problem_updates_existing_entry(self):
        sheet = Sheet.objects.create(name="Mine", owner=self.user)
        self.client.force_authenticate(user=self.user)
        self.client.post(
            f"/api/sheets/{sheet.id}/problems/",
            {"problem_id": self.problem.id, "order": 1},
        )
        self.client.post(
            f"/api/sheets/{sheet.id}/problems/",
            {"problem_id": self.problem.id, "order": 5},
        )
        self.assertEqual(
            SheetProblem.objects.filter(sheet=sheet, problem=self.problem).count(), 1
        )
        entry = SheetProblem.objects.get(sheet=sheet, problem=self.problem)
        self.assertEqual(entry.order, 5)

    def test_cannot_update_others_public_sheet(self):
        sheet = Sheet.objects.create(name="Public", owner=self.other_user, is_public=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f"/api/sheets/{sheet.id}/", {"name": "Hijacked"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        sheet.refresh_from_db()
        self.assertEqual(sheet.name, "Public")

    def test_cannot_delete_others_sheet(self):
        sheet = Sheet.objects.create(name="Public", owner=self.other_user, is_public=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/sheets/{sheet.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Sheet.objects.filter(id=sheet.id).exists())

    def test_owner_can_update_and_delete_own_sheet(self):
        sheet = Sheet.objects.create(name="Mine", owner=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f"/api/sheets/{sheet.id}/", {"name": "Renamed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sheet.refresh_from_db()
        self.assertEqual(sheet.name, "Renamed")

        response = self.client.delete(f"/api/sheets/{sheet.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sheet.objects.filter(id=sheet.id).exists())


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

    def test_stats_by_difficulty(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/stats/")
        self.assertEqual(response.data["by_difficulty"][Problem.Difficulty.EASY], 1)
        self.assertEqual(response.data["by_difficulty"][Problem.Difficulty.MEDIUM], 1)

    def test_stats_by_topic_only_counts_solved(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/stats/")
        by_topic = {entry["problem__topics__name"]: entry["count"] for entry in response.data["by_topic"]}
        self.assertEqual(by_topic, {"Arrays": 1})
