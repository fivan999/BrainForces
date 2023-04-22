import django.contrib

import quiz.models


@django.contrib.admin.register(quiz.models.Quiz)
class QuizAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Quiz в админке"""

    list_display = (
        'id',
        'name',
        'start_time',
        'is_rated',
        'is_private',
        'is_ended',
        'is_published',
    )
    list_display_links = ('id',)
    list_editable = ('is_rated', 'is_ended', 'is_published')
    list_filter = ('is_published',)


class VariantInline(django.contrib.admin.TabularInline):
    """Вспомогательная модель для отображения вариантов ответа вопросов"""

    model = quiz.models.Variant
    extra = 1


@django.contrib.admin.register(quiz.models.Question)
class QuestionAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Question в админке"""

    inlines = [
        VariantInline,
    ]
    list_display = (
        'id',
        'name',
        'text',
    )
    list_display_links = ('id',)


@django.contrib.admin.register(quiz.models.Tag)
class TagAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Tag в админке"""

    list_display = (
        'name',
        'is_published',
    )
    list_editable = ('is_published',)
    list_display_links = ('name',)


@django.contrib.admin.register(quiz.models.UserAnswer)
class UserAnswerAdmin(django.contrib.admin.ModelAdmin):
    """отображение ответа в админке"""

    list_display = (
        'id',
        'user',
        'question',
        'is_correct',
    )
    list_display_links = ('id',)


@django.contrib.admin.register(quiz.models.QuizResults)
class QuizResultsAdmin(django.contrib.admin.ModelAdmin):
    """отображение результатов в админке"""

    list_display = ('id', 'user', 'quiz', 'place')
    list_display_links = ('id',)
