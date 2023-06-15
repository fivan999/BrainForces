import ckeditor_uploader.fields
import taggit.managers
import taggit.models

import django.core.validators
import django.db.models
import django.shortcuts
import django.urls
import django.utils.encoding
import django.utils.timezone

import organization.models
import quiz.managers
import users.models


class Quiz(django.db.models.Model):
    """модель викторины"""

    objects = quiz.managers.QuizManager()

    creator = django.db.models.ForeignKey(
        users.models.User,
        verbose_name='создатель',
        on_delete=django.db.models.CASCADE,
        related_name='user_creator',
        help_text='Пользователь, который создал викторину',
        null=True,
    )

    name = django.db.models.CharField(
        max_length=50,
        help_text='Напишите название викторины',
        verbose_name='название викторины',
        null=False,
    )

    description = ckeditor_uploader.fields.RichTextUploadingField(
        help_text='Создайте описание для Вашей викторины',
        verbose_name='описание',
    )

    start_time = django.db.models.DateTimeField(
        help_text='Выберите время начала викторины. Часовой пояс - UTC+03:00',
        null=True,
        blank=True,
        verbose_name='стартовое время',
    )

    duration = django.db.models.PositiveIntegerField(
        help_text='Укажите продолжительность викторины в минутах',
        verbose_name='продолжительность',
        validators=[django.core.validators.MinValueValidator(10)],
        default=10,
    )

    is_rated = django.db.models.BooleanField(
        verbose_name='рейтинговая',
        help_text='Изменяется ли рейтинг пользователя после данной викторины',
        default=True,
    )

    organized_by = django.db.models.ForeignKey(
        organization.models.Organization,
        verbose_name='организация',
        help_text='Организация, подготовившая викторину',
        on_delete=django.db.models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='quizzes',
    )

    is_private = django.db.models.BooleanField(
        verbose_name='приватная',
        help_text='Приватная викторина или нет',
        default=False,
    )

    is_ended = django.db.models.BooleanField(
        verbose_name='итоги подведены',
        help_text='Подведены итоги или нет',
        default=False,
    )

    is_published = django.db.models.BooleanField(
        verbose_name='опубликована',
        help_text='Опубликована или нет',
        default=True,
    )

    class Meta:
        verbose_name = 'викторина'
        verbose_name_plural = 'викторины'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]

    def get_absolute_url(self) -> str:
        """ссылка на викторину"""
        return django.urls.reverse_lazy(
            'quiz:quiz_detail', kwargs={'pk': self.pk}
        )

    def get_quiz_status(self) -> int:
        """статус викторины"""
        now_datetime = django.utils.timezone.now()
        if now_datetime < self.start_time:
            return 1
        elif (
            self.start_time
            < now_datetime
            < self.start_time
            + django.utils.timezone.timedelta(minutes=self.duration)
        ):
            return 2
        else:
            return 3

    def get_status_display(self) -> str:
        """получаем текстовое представление статусов"""
        text_statuses = {1: 'Не начата', 2: 'Идет', 3: 'Закончена'}
        return text_statuses[self.get_quiz_status()]

    def description_to_string_for_elastic(self) -> str:
        """
        elastic не может делать поиск по RichTextUploadingField сам,
        поэтому прописываем его сами
        """
        return self.description

    def organized_by_to_string_for_elastic(self) -> str:
        """
        elastic не может делать поиск по FK сам,
        поэтому прописываем его сами
        """
        return self.organized_by.name


class QuizResults(django.db.models.Model):
    """модель результатов викторины"""

    objects = quiz.managers.QuizResultsManager()

    user = django.db.models.ForeignKey(
        users.models.User,
        verbose_name='пользователь',
        help_text='Пользователь, участвующий в викторине',
        related_name='results',
        on_delete=django.db.models.CASCADE,
    )

    quiz = django.db.models.ForeignKey(
        Quiz,
        verbose_name='викторина',
        help_text='Викторина, к которой относится результат',
        on_delete=django.db.models.CASCADE,
        related_name='results',
    )

    rating_before = django.db.models.PositiveIntegerField(
        verbose_name='рейтинг до',
        help_text='Рейтинг пользователя до участия в викторине',
        default=0,
    )

    rating_after = django.db.models.PositiveIntegerField(
        verbose_name='рейтинг после',
        help_text='Рейтинг пользователя после участия в викторине',
        default=0,
    )

    solved = django.db.models.PositiveIntegerField(
        verbose_name='задачи', help_text='Верно решенные задачи', default=0
    )

    place = django.db.models.PositiveIntegerField(
        verbose_name='место',
        help_text='Место пользователя в викторине',
        default=0,
    )

    class Meta:
        verbose_name = 'результат'
        verbose_name_plural = 'результаты'

    def __str__(self) -> str:
        """строковое представление"""
        return f'Результат {self.pk}'


class Question(django.db.models.Model):
    """модель вопроса"""

    objects = quiz.managers.QuestionManager()

    name = django.db.models.CharField(
        max_length=100,
        help_text='Напишите название вопроса',
        verbose_name='название вопроса',
    )

    text = ckeditor_uploader.fields.RichTextUploadingField(
        help_text='Напишите вопрос', verbose_name='текст'
    )

    quiz = django.db.models.ForeignKey(
        Quiz,
        verbose_name='викторина',
        on_delete=django.db.models.CASCADE,
        related_name='quiz_question',
        help_text='викторина, к которой относится вопрос',
    )

    difficulty = django.db.models.PositiveSmallIntegerField(
        verbose_name='сложность',
        help_text='сложность вопроса',
        default=0,
        validators=[django.core.validators.MaxValueValidator(10)],
    )

    tags = taggit.managers.TaggableManager(
        verbose_name='теги',
        help_text='список тегов, разделенных запятой',
        related_name='questions',
        to=taggit.models.Tag,
    )

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]

    def get_absolute_url(self) -> str:
        """путь к question detail"""
        return django.urls.reverse_lazy(
            'quiz:question_detail',
            kwargs={'pk': self.quiz.pk, 'question_pk': self.pk},
        )


class Variant(django.db.models.Model):
    """модель варианта ответа"""

    text = django.db.models.CharField(
        max_length=150,
        help_text='Напишите вариант ответа',
        verbose_name='ответ',
    )

    question = django.db.models.ForeignKey(
        Question,
        verbose_name='вопрос',
        on_delete=django.db.models.CASCADE,
        related_name='variants',
        help_text='вопрос, к которому относится вариант ответа',
    )

    is_correct = django.db.models.BooleanField(
        verbose_name='правильность варианта',
        help_text='правильный вариант или нет',
        default=False,
    )

    class Meta:
        verbose_name = 'вариант ответа'
        verbose_name_plural = 'варианты ответов'

    def __str__(self) -> str:
        """строковое представление"""
        return self.text[:20]


class UserAnswer(django.db.models.Model):
    """модель ответа пользователя"""

    objects = quiz.managers.UserAnswerManager()

    user = django.db.models.ForeignKey(
        users.models.User,
        verbose_name='пользователь',
        on_delete=django.db.models.CASCADE,
        related_name='answers',
        help_text='пользователь, который дал ответ',
    )

    question = django.db.models.ForeignKey(
        Question,
        verbose_name='вопрос',
        help_text='вопрос на который пользователь дал ответ',
        related_name='answers',
        on_delete=django.db.models.CASCADE,
    )

    is_correct = django.db.models.BooleanField(
        verbose_name='правильность ответа',
        help_text='правильный ответ или нет',
    )

    time_answered = django.db.models.DateTimeField(
        verbose_name='время',
        help_text='Время, когда пользователь ответил на вопрос',
        auto_now_add=True,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'ответ пользователя'
        verbose_name_plural = 'ответы пользователей'

    def __str__(self) -> str:
        """строковое представление"""
        return f'Ответ {self.pk}'
