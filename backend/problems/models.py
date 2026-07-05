from django.conf import settings
from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    title = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
    source = models.CharField(max_length=100, blank=True)
    topics = models.ManyToManyField(Topic, related_name="problems", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Sheet(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sheets"
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    problems = models.ManyToManyField(
        Problem, through="SheetProblem", related_name="sheets"
    )

    def __str__(self):
        return self.name


class SheetProblem(models.Model):
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("sheet", "problem")


class UserProblemStatus(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        ATTEMPTED = "attempted", "Attempted"
        SOLVED = "solved", "Solved"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="problem_statuses"
    )
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="user_statuses"
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.TODO
    )
    notes = models.TextField(blank=True)
    code_snippet = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "problem")
        verbose_name_plural = "user problem statuses"

    def __str__(self):
        return f"{self.user} - {self.problem} - {self.status}"
