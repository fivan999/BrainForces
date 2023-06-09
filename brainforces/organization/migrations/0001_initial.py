# Generated by Django 3.2.16 on 2023-04-09 14:24

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название организации', max_length=100, verbose_name='название')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(help_text='Описание организации', verbose_name='описание')),
            ],
            options={
                'verbose_name': 'организация',
                'verbose_name_plural': 'организации',
            },
        ),
        migrations.CreateModel(
            name='OrganizationToUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Участник'), (2, 'Админ'), (3, 'Создатель')], default=1, help_text='Роль пользователя в организации', verbose_name='роль')),
                ('organization', models.ForeignKey(help_text='Организация, в которой состоит пользователь', on_delete=django.db.models.deletion.CASCADE, related_name='users', to='organization.organization', verbose_name='организация')),
                ('user', models.ForeignKey(help_text='Пользователь, состоящий в организации', on_delete=django.db.models.deletion.CASCADE, related_name='organizations', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'участник',
                'verbose_name_plural': 'участники',
            },
        ),
    ]
