import os
import pathlib

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
    'taggit',
    'django.contrib.postgres',
    'django_filters',
    'social_django',
    'django_extensions',
    'django_elasticsearch_dsl',
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
    'social_django.middleware.SocialAuthExceptionMiddleware',
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

AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.yandex.YandexOAuth2',
]

SOCIAL_AUTH_VK_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_VK_OAUTH2_KEY')
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_VK_OAUTH2_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv(
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'
)

SOCIAL_AUTH_YANDEX_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_YANDEX_OAUTH2_KEY')
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = os.getenv(
    'SOCIAL_AUTH_YANDEX_OAUTH2_SECRET'
)

SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'users.pipelines.create_profile_for_social_authenticated_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
]

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

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': f"{os.getenv('ELASTICSEARCH_HOST', default='localhost')}"
                 f":{os.getenv('ELASTICSEARCH_PORT', default='9200')}"
    },
}

print(ELASTICSEARCH_DSL)
