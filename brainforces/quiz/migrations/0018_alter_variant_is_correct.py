# Generated by Django 3.2.16 on 2023-04-17 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0017_merge_20230417_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='is_correct',
            field=models.BooleanField(default=False, help_text='правильный вариант или нет', verbose_name='правильность варианта'),
        ),
    ]
