# Generated by Django 3.2.16 on 2023-04-13 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0012_rename_organizated_by_quiz_organized_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='is_private',
            field=models.BooleanField(default=False, help_text='приватное соревнование или нет', verbose_name='приватная'),
        ),
    ]