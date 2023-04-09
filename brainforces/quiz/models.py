import ckeditor_uploader.fields
import organization.models

import django.db.models

import quiz.managers
import users.models


class Tag(django.db.models.Model):
    """модель тега для викторины"""

    is_published = django.db.models.BooleanField(
        verbose_name='опубликован',
        help_text='Опубликован тег или нет',
        default=True,
    )
    name = django.db.models.CharField(
        verbose_name='имя тега', help_text='Введите имя тега', max_length=150
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        """строковое представление"""

        return self.name[:20]


class Quiz(django.db.models.Model):
    """модель викторины"""

    objects = quiz.managers.QuizManager()

    class Statuses(django.db.models.IntegerChoices):
        NOT_STARTED = 1, 'Не начата'
        GOES_ON = 2, 'Идет'
        FINISHED = 3, 'Закончена'

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
    )

    status = django.db.models.IntegerField(
        choices=Statuses.choices,
        help_text='Поставьте статус викторины',
        default=1,
        verbose_name='статус',
    )

    description = ckeditor_uploader.fields.RichTextUploadingField(
        help_text='Создайте описание для Вашей викторины',
        verbose_name='описание',
    )

    start_time = django.db.models.DateTimeField(
        help_text='Назначьте стартовое время для Вашей викторины',
        null=True,
        blank=True,
        verbose_name='стартовое время',
    )

    duration = django.db.models.IntegerField(
        help_text='Укажите продолжительность викторины в минутах',
        null=True,
        blank=True,
        verbose_name='продолжительность',
    )

    is_rated = django.db.models.BooleanField(
        verbose_name='рейтинговая',
        help_text='Изменяется ли рейтинг пользователя после данной викторины',
        default=True,
    )

    organizated_by = django.db.models.ForeignKey(
        organization.models.Organization,
        verbose_name='организация',
        help_text='Организация, подготовившая викторину',
        on_delete=django.db.models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='quizzes'
    )

    class Meta:
        verbose_name = 'викторина'
        verbose_name_plural = 'викторины'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]


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
        default=1,
    )

    tags = django.db.models.ManyToManyField(
        Tag,
        related_name='questions',
        verbose_name='теги вопроса',
        help_text='выберите теги вопроса',
        blank=True,
    )

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]


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
        related_name='useranswer_user',
        help_text='пользователь, который дал ответ',
    )

    question = django.db.models.ForeignKey(
        Question,
        verbose_name='вопрос',
        help_text='вопрос на который пользователь дал ответ',
        related_name='useranswer_question',
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
