# Generated by Django 3.2.16 on 2023-04-18 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0011_alter_organizationtouser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationpost',
            name='is_private',
            field=models.BooleanField(default=False, help_text='Приватный пост или нет', verbose_name='приватный'),
        ),
    ]
