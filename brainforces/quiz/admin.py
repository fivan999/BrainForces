import quiz.models

import django.contrib


@django.contrib.admin.register(quiz.models.Quiz)
class QuizAdmin(django.contrib.admin.ModelAdmin):
    """отображение модели Quiz в админке"""

    list_display = (
        'id',
        'name',
        'status',
        'start_time',
        'duration',
    )
    list_display_links = ('id',)
    list_editable = ('status',)


class VariantInline(django.contrib.admin.TabularInline):
    """Вспомогательная модель для отображения вариантов ответа вопросов"""

    model = quiz.models.Variant


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
