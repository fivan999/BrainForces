import secrets
import typing

import sorl.thumbnail
import transliterate

import django.db.models


def generate_image_path(obj: django.db.models.Model, filename: str) -> str:
    """делаем путь к картинке"""
    filename = transliterate.translit(filename, 'ru', reversed=True)
    filename = (
        filename[: filename.rfind('.')]
        + secrets.token_hex(6)
        + filename[filename.rfind('.') :]
    )
    return f'images/{filename}'


class AbstractImageModel(django.db.models.Model):
    """абсрактная модель с картинкой"""

    image = django.db.models.ImageField(
        verbose_name='картинка',
        help_text='Загрузите картинку',
        upload_to='images',
    )

    def get_image_50x50(self) -> typing.Any:
        """делаем миниатюру"""
        return sorl.thumbnail.get_thumbnail(
            self.image, '50x50', crop='center', quality=60
        )

    class Meta:
        abstract = True
