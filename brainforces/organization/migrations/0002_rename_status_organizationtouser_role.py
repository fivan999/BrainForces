# Generated by Django 3.2.16 on 2023-04-09 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organizationtouser',
            old_name='status',
            new_name='role',
        ),
    ]
