# Generated by Django 3.2.16 on 2023-04-13 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0013_quiz_is_private'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='is_private',
            field=models.BooleanField(default=False, help_text='Приватная викторина или нет', verbose_name='приватная'),
        ),
    ]
