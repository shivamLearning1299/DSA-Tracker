from rest_framework import serializers

from .models import Problem, Sheet, SheetProblem, Topic, UserProblemStatus


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "name"]


class UserProblemStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProblemStatus
        fields = ["id", "problem", "status", "notes", "code_snippet", "last_updated"]
        read_only_fields = ["id", "last_updated"]


class ProblemSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(), many=True, write_only=True, source="topics", required=False
    )
    status = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "url",
            "difficulty",
            "source",
            "topics",
            "topic_ids",
            "created_at",
            "status",
        ]

    def get_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        status_obj = obj.user_statuses.filter(user=request.user).first()
        return status_obj.status if status_obj else UserProblemStatus.Status.TODO


class SheetProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)
    problem_id = serializers.PrimaryKeyRelatedField(
        queryset=Problem.objects.all(), write_only=True, source="problem"
    )

    class Meta:
        model = SheetProblem
        fields = ["id", "problem", "problem_id", "order"]


class SheetSerializer(serializers.ModelSerializer):
    sheet_problems = SheetProblemSerializer(
        source="sheetproblem_set", many=True, read_only=True
    )

    class Meta:
        model = Sheet
        fields = ["id", "name", "is_public", "created_at", "sheet_problems"]
        read_only_fields = ["id", "created_at"]
