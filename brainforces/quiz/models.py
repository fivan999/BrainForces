from django.db import models


class Quiz(models.Model):
    """модель викторины"""

    class Statuses(models.IntegerChoices):
        NOT_STARTED = 1, 'Не начата'
        GOES_ON = 2, 'Идет'
        FINISHED = 3, 'Закончена'

    # creator = models.ForeignKey(
    #     users.models.User,
    #     verbose_name='пользователь',
    #     on_delete=models.CASCADE,
    #     related_name='user_creator',
    #     help_text='пользователь, который создал викторину'
    # )

    name = models.CharField(
        'название викторины',
        max_length=50,
        help_text='Напишите название викторины'
    )

    status = models.IntegerField(
        'статус',
        choices=Statuses.choices,
        help_text='Поставьте статус викторины',
        default=1
    )

    description = models.TextField(
        'описание',
        help_text='Создайте описание для Вашей викторины'
    )

    start_time = models.DateTimeField(
        'стартовое время',
        help_text='Назначьте стартовое время для Вашей викторины',
        null=True, 
        blank=True
    )

    duration = models.IntegerField(
        'продолжительность',
        help_text='Укажите продолжительность викторины в минутах',
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = 'викторина'
        verbose_name_plural = 'викторины'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]


class Question(models.Model):
    """модель вопроса"""

    name = models.CharField(
        'название вопроса',
        max_length=100,
        help_text='Напишите название вопроса'
    )

    text = models.TextField(
        'текст',
        help_text='Напишите вопрос'
    )
    
    quiz = models.ForeignKey(
        Quiz,
        verbose_name='викторина',
        on_delete=models.CASCADE,
        related_name='quiz_question',
        help_text='викторина, к которой относится вопрос'
    )

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self) -> str:
        """строковое представление"""
        return self.name[:20]
    

class Answer(models.Model):
    """модель варианта ответа"""

    text = models.CharField(
        'ответ',
        max_length=150,
        help_text='Напишите вариант ответа'
    )
    
    question = models.ForeignKey(
        Question,
        verbose_name='вопрос',
        on_delete=models.CASCADE,
        related_name='question_answer',
        help_text='вопрос, к которому относится вариант ответа'
    )

    class Meta:
        verbose_name = 'вариант ответа'
        verbose_name_plural = 'варианты ответов'

    def __str__(self) -> str:
        """строковое представление"""
        return self.text[:20]
