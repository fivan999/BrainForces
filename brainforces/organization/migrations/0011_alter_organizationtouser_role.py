# Generated by Django 3.2.16 on 2023-04-15 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0010_alter_organizationpost_posted_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationtouser',
            name='role',
            field=models.IntegerField(choices=[(0, 'Приглашен'), (1, 'Участник'), (2, 'Админ'), (3, 'Создатель')], default=1, help_text='Роль пользователя в организации', verbose_name='роль'),
        ),
    ]
