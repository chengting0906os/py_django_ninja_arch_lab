"""Django settings for the shopping system project.

SECURITY NOTES FOR PRODUCTION:
- SECRET_KEY: MUST be strong random value (use secrets.token_urlsafe(50))
- DEBUG: MUST be False in production
- ALLOWED_HOSTS: MUST specify exact domains, never use ['*']
- Database credentials: Store in environment variables or secrets manager
- CORS_ALLOWED_ORIGINS: Restrict to known frontend domains only
"""

from pathlib import Path

from src.platform.config.env_config import env_config


BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep SECRET_KEY secret! Use environment variable in production.
# Generate new key: python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY = env_config.SECRET_KEY.get_secret_value()

# SECURITY WARNING: Don't run with DEBUG=True in production!
# Set DEBUG=False in production to prevent information disclosure.
DEBUG = env_config.DEBUG

# SECURITY WARNING: Update ALLOWED_HOSTS for production!
# Example: ALLOWED_HOSTS = ['api.yourdomain.com', 'www.yourdomain.com']
# Never use ['*'] in production - it allows Host header attacks.
ALLOWED_HOSTS: list[str] = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'ninja_extra',
    'src.platform',
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

ROOT_URLCONF = 'src.platform.config.urls'
ASGI_APPLICATION = 'src.platform.config.asgi.application'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_config.POSTGRES_DB,
        'USER': env_config.POSTGRES_USER,
        'PASSWORD': env_config.POSTGRES_PASSWORD.get_secret_value(),
        'HOST': env_config.POSTGRES_SERVER,
        'PORT': env_config.POSTGRES_PORT,
        # TODO: Enable SSL in production
        # 'OPTIONS': {'sslmode': 'require'},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS: list[Path] = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# app setting
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'platform.User'

MIGRATION_MODULES = {
    'models': 'src.platform.migrations',
}


NINJA_EXTRA = {
    'app_name': 'api',
    'INJECTOR_MODULES': ['src.platform.config.di.ApplicationModule'],
}

# SECURITY WARNING: CORS configuration for production
# CORS_ALLOW_CREDENTIALS=True requires specific origins, not wildcard
# Only allow trusted frontend domains in CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env_config.BACKEND_CORS_ORIGINS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# SECURITY: Cookie settings for CSRF and session protection
# SECURE=True requires HTTPS (enforced in production when DEBUG=False)
# SameSite='None' for cross-origin requests (requires Secure=True)
# Consider SameSite='Strict' or 'Lax' if same-origin only
SESSION_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
SESSION_COOKIE_SECURE = not DEBUG  # Requires HTTPS in production
CSRF_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
CSRF_COOKIE_SECURE = not DEBUG  # Requires HTTPS in production

# TODO: Additional production security settings to consider:
# SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
# SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
# CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF token

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
