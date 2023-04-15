# Generated by Django 3.2.16 on 2023-04-13 21:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0008_auto_20230413_2104'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='organizationpost',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='commenttoorganizationpost',
            name='post',
            field=models.ForeignKey(help_text='Пост, к которому оставлен комментарий', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='organization.organizationpost', verbose_name='пост'),
        ),
        migrations.AlterField(
            model_name='commenttoorganizationpost',
            name='user',
            field=models.ForeignKey(help_text='Пользователь, котрый оставил комментарий', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        migrations.AlterField(
            model_name='organizationpost',
            name='posted_by',
            field=models.ForeignKey(help_text='организация, написавшая пост', on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='organization.organization', verbose_name='организация'),
        ),
    ]