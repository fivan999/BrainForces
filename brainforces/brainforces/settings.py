import os
import pathlib
import sys

import dotenv

import django.contrib.messages


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

dotenv.load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', default='default')

YES_OPTIONS = ('true', 'y', '1', 'yes')

DEBUG = os.getenv('DEBUG', default='True').lower() in YES_OPTIONS

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default='127.0.0.1').split()

INSTALLED_APPS = [
    'quiz.apps.QuizConfig',
    'homepage.apps.HomepageConfig',
    'archive.apps.ArchiveConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',
    'organization.apps.OrganizationConfig',
    'about.apps.AboutConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_dump_load_utf8',
    'sorl.thumbnail',
    'django_cleanup.apps.CleanupConfig',
    'ckeditor',
    'ckeditor_uploader',
    'widget_tweaks',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = os.getenv('INTERNAL_IPS', default='127.0.0.1').split()

ROOT_URLCONF = 'brainforces.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'brainforces.wsgi.application'

DATABASES = dict()

if (
    'test' in sys.argv
    or not os.getenv('USE_POSTGRES', default='False').lower() in YES_OPTIONS
):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
    }
    if os.getenv('DB_PORT', default=''):
        DATABASES['default']['PORT'] = os.getenv('DB_PORT')


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.NumericPasswordValidator',
    },
]

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

USER_IS_ACTIVE = (
    os.getenv('USER_IS_ACTIVE', default='False').lower() in YES_OPTIONS
)

AUTHENTICATION_BACKENDS = ['users.backends.EmailBackend']
LOGIN_ATTEMPTS = int(os.environ.get('LOGIN_ATTEMPTS', default=3))


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_DIRS = [
    BASE_DIR / 'static_dev',
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

CKEDITOR_UPLOAD_PATH = 'uploads/'

AUTH_USER_MODEL = 'users.User'

CKEDITOR_CONFIGS = {
    'default': {
        'width': '100%',
        'skin': 'moono-lisa',
        'toolbar_Basic': [['Source', '-', 'Bold', 'Italic']],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'clipboard', 'items': ['Undo', 'Redo']},
            {
                'name': 'basicstyles',
                'items': [
                    'Bold',
                    'Italic',
                    'Underline',
                    'Strike',
                    'Subscript',
                    'Superscript',
                ],
            },
            {
                'name': 'paragraph',
                'items': [
                    'NumberedList',
                    'BulletedList',
                    '-',
                    'Outdent' 'Indent',
                    '-',
                    'JustifyLeft',
                    'JustifyCenter',
                    'JustifyRight',
                    'JustifyBlock',
                    '-',
                    'BidiLtr',
                    'BidiRtl',
                ],
            },
            {
                'name': 'insert',
                'items': [
                    'Image',
                    'Flash',
                    'Table',
                    'HorizontalRule',
                    'Smiley',
                    'SpecialChar',
                ],
            },
            {
                'name': 'styles',
                'items': ['Styles', 'Format', 'Font', 'FontSize'],
            },
            {'name': 'colors', 'items': ['TextColor']},
            {
                'name': 'yourcustomtools',
                'items': [
                    'Maximize',
                ],
            },
        ],
        'toolbar': 'YourCustomToolbarConfig',
        'tabSpaces': 4,
        'extraPlugins': ','.join(
            [
                'uploadimage',
                'div',
                'autolink',
                'autoembed',
                'embedsemantic',
                'autogrow',
                'widget',
                'lineutils',
                'clipboard',
                'dialog',
                'dialogui',
                'elementspath',
            ]
        ),
    }
}


if os.getenv('USE_SMTP', default='False').lower() in YES_OPTIONS:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = os.getenv('EMAIL_PORT')
    EMAIL_USE_TLS = (
        os.getenv('EMAIL_USE_TLS', default='true').lower() in YES_OPTIONS
    )
    EMAIL_USE_SSL = (
        os.getenv('EMAIL_USER_SSL', default='false').lower() in YES_OPTIONS
    )
    if EMAIL_USE_TLS:
        EMAIL_USE_SSL = False
    if EMAIL_USE_SSL:
        EMAIL_USE_TLS = False
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    SERVER_EMAIL = EMAIL_HOST_USER
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
else:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

PASSWORD_RESET_TIMEOUT = 43200

MESSAGE_TAGS = {
    django.contrib.messages.constants.DEBUG: 'alert-secondary',
    django.contrib.messages.constants.INFO: 'alert-info',
    django.contrib.messages.constants.SUCCESS: 'alert-success',
    django.contrib.messages.constants.WARNING: 'alert-warning',
    django.contrib.messages.constants.ERROR: 'alert-danger',
}
