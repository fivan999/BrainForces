# Generated by Django 3.2.16 on 2023-07-05 20:19

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0019_alter_organizationpost_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationpost',
            name='text',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Текст поста', max_length=1000, verbose_name='текст'),
        ),
    ]
