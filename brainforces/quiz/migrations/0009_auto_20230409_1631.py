# Generated by Django 3.2.16 on 2023-04-09 13:31

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_auto_20230407_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='text',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Напишите вопрос', verbose_name='текст'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Создайте описание для Вашей викторины', verbose_name='описание'),
        ),
    ]
