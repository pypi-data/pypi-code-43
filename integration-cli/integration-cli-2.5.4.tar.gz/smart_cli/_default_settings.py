import os
from event_monitoring import EMConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'z4iy1l-@l=rk4+iqis*c5s2thix0wh5sw%j4=&64&7r@74jwgq'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'api',
    'methods',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '__base_project_name__.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = '__base_project_name__.wsgi.application'
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

"""UNCOMENT THIS FOR DATABASE"""
# DATABASES = {
#     'default': {        
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'test_db',
#         'USER': 'admin',
#         'PASSWORD': 'password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

SYSTEM_EVENT_TOKEN = ''
SYSTEM_EVENT_NAME = ''
SYSTEM_EVENT_URL = 'https://1x907smcp2.execute-api.eu-central-1.amazonaws.com/event_monitoring/'
EMConfig(
    SYSTEM_EVENT_TOKEN=SYSTEM_EVENT_TOKEN,
    SYSTEM_EVENT_NAME=SYSTEM_EVENT_NAME,
    SYSTEM_EVENT_URL=SYSTEM_EVENT_URL,
)

DASHBOARD_URL = "https://9tnvnh6ri0.execute-api.eu-central-1.amazonaws.com/dashboard/"
BUCKET_NAME = 'zappa-fullbucket'
EXECUTE_TOKEN = '&g(#ul0wcz07f++(qk6bs5!zs(uj!y))@c@bysgfspag(%g50a'
