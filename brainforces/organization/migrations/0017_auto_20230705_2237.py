# Generated by Django 3.2.16 on 2023-07-05 19:37

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0016_auto_20230605_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Описание организации', max_length=500, verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(help_text='Название организации', max_length=50, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='organizationpost',
            name='text',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Текст поста', max_length=500, verbose_name='текст'),
        ),
    ]
