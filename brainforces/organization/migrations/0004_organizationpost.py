# Generated by Django 3.2.16 on 2023-04-13 14:24

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_auto_20230412_2349'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название объявления', max_length=150, verbose_name='название')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(help_text='Текст поста', verbose_name='текст')),
                ('posted_by', models.ForeignKey(help_text='организация, написавшая пост', on_delete=django.db.models.deletion.CASCADE, to='organization.organization', verbose_name='организация')),
            ],
        ),
    ]
