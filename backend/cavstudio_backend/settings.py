"""
Django settings for cavstudio_backend project.
"""

import os
import platformdirs

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_DATA_DIR = platformdirs.user_data_dir('CAVstudio', 'Nord Projects')

# we don't need a secret key, as we're always serving localhost
SECRET_KEY = 'a-not-very-secret-key'

DEBUG = (os.environ.get('DEBUG', 'True') == 'True')
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'cavstudio_backend',
    'cavstudio_db',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# if DEBUG:
#     MIDDLEWARE.append('pyinstrument.middleware.ProfilerMiddleware')
#     PYINSTRUMENT_PROFILE_DIR = 'profile_output'

ROOT_URLCONF = 'cavstudio_backend.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

WSGI_APPLICATION = 'cavstudio_backend.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_CAV_CONTENT_URL = '/static-cav-content/'
STATIC_CAV_CONTENT_ROOT = os.path.join(BASE_DIR, 'static-cav-content')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(USER_DATA_DIR, 'media')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(USER_DATA_DIR, 'database.db'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'cavstudio_backend.auth.LocalhostAuthentication',
    ],
    'UNAUTHENTICATED_USER': None,
}

CORS_ORIGIN_ALLOW_ALL = True
