from django.contrib import admin

from .models import Problem, Sheet, SheetProblem, Topic, UserProblemStatus

admin.site.register(Topic)
admin.site.register(Problem)
admin.site.register(Sheet)
admin.site.register(SheetProblem)
admin.site.register(UserProblemStatus)
