# Generated by Django 3.2.16 on 2023-04-17 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0019_auto_20230417_2330'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='is_ended',
            field=models.BooleanField(default=False, help_text='Подведены итоги или нет', verbose_name='итоги подведены'),
        ),
    ]
