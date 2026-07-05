from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Problem, Sheet, SheetProblem, Topic, UserProblemStatus
from .serializers import (
    ProblemSerializer,
    SheetProblemSerializer,
    SheetSerializer,
    TopicSerializer,
    UserProblemStatusSerializer,
)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all().prefetch_related("topics")
    serializer_class = ProblemSerializer
    filterset_fields = ["difficulty", "source"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=True, methods=["post"], url_path="status")
    def set_status(self, request, pk=None):
        problem = self.get_object()
        status_value = request.data.get("status", UserProblemStatus.Status.TODO)
        notes = request.data.get("notes", "")
        code_snippet = request.data.get("code_snippet", "")

        obj, _ = UserProblemStatus.objects.update_or_create(
            user=request.user,
            problem=problem,
            defaults={
                "status": status_value,
                "notes": notes,
                "code_snippet": code_snippet,
            },
        )
        return Response(UserProblemStatusSerializer(obj).data)


class SheetViewSet(viewsets.ModelViewSet):
    serializer_class = SheetSerializer

    def get_queryset(self):
        if self.action in ("update", "partial_update", "destroy"):
            return Sheet.objects.filter(owner=self.request.user)
        return Sheet.objects.filter(
            Q(owner=self.request.user) | Q(is_public=True)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="problems")
    def add_problem(self, request, pk=None):
        sheet = self.get_object()
        problem_id = request.data.get("problem_id")
        order = request.data.get("order", 0)
        sheet_problem, _ = SheetProblem.objects.update_or_create(
            sheet=sheet, problem_id=problem_id, defaults={"order": order}
        )
        return Response(SheetProblemSerializer(sheet_problem).data)


class StatsView(viewsets.ViewSet):
    def list(self, request):
        statuses = UserProblemStatus.objects.filter(user=request.user)

        by_status = dict(
            statuses.values_list("status").annotate(count=Count("id")).order_by()
        )
        by_difficulty = dict(
            statuses.values_list("problem__difficulty").annotate(count=Count("id")).order_by()
        )
        by_topic = list(
            statuses.filter(status=UserProblemStatus.Status.SOLVED)
            .values("problem__topics__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response(
            {
                "by_status": by_status,
                "by_difficulty": by_difficulty,
                "by_topic": by_topic,
                "total_solved": statuses.filter(
                    status=UserProblemStatus.Status.SOLVED
                ).count(),
            }
        )
