# Generated by Django 3.2.16 on 2023-04-24 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0023_quiz_is_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='is_published',
            field=models.BooleanField(default=True, help_text='Опубликована или нет', verbose_name='опубликована'),
        ),
    ]