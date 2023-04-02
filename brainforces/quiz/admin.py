import quiz.models

import django.contrib


@django.contrib.admin.register(quiz.models.Quiz)
class QuizAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Quiz в админке"""

    list_display = (
        'id',
        'name',
        'status',
        'description',
        'start_time',
        'duration',
    )
    list_display_links = ('id',)
    list_editable = ('status',)


@django.contrib.admin.register(quiz.models.Question)
class QuestionAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Question в админке"""

    list_display = (
        'id',
        'name',
        'text',
    )
    list_display_links = ('id',)


@django.contrib.admin.register(quiz.models.Answer)
class AnswerAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Answer в админке"""

    list_display = (
        'id',
        'text',
    )
    list_display_links = ('id',)
