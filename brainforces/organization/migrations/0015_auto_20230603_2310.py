# Generated by Django 3.2.16 on 2023-06-03 20:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0014_organizationpost_users_liked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizationpost',
            name='users_liked',
        ),
        migrations.CreateModel(
            name='OrganizationPostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(help_text='пост, под который поставлен лайк', on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='organization.organizationpost', verbose_name='пост')),
                ('user', models.ForeignKey(help_text='пользователь, поставивший лайк', on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL, verbose_name='пользователь')),
            ],
        ),
    ]