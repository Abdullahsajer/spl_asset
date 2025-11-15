import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# تحميل متغيرات البيئة
load_dotenv()

# ================================
# المسار الأساسي
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# مفاتيح النظام
# ================================
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_RENDER")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ================================
# التطبيقات
# ================================
INSTALLED_APPS = [
    # ⭐ Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ⭐ Project Apps
    'accounts_app.apps.AccountsAppConfig',
    'locations_app.apps.LocationsAppConfig',
    'assets_app.apps.AssetsAppConfig',
    'inventory_app.apps.InventoryAppConfig',
    'reports_app.apps.ReportsAppConfig',
]

# ================================
# Middleware
# ================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # ⭐ WhiteNoise لتقديم الملفات الثابتة في Render
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    # ⭐ دعم العربية
    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ================================
# URLs / WSGI
# ================================
ROOT_URLCONF = 'splasset.urls'
WSGI_APPLICATION = 'splasset.wsgi.application'

# ================================
# Templates
# ================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # ⭐ تمرير مجموعات المستخدم للقوالب
                'splasset.context_processors.user_groups',
                'splasset.context_processors.pending_sessions',
            ],
        },
    },
]

# ================================
# قاعدة البيانات — Render (PostgreSQL)
# ================================
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
}

# ================================
# التحقق من كلمات المرور
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ================================
# اللغة والتوقيت
# ================================
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# ================================
# Static files — WhiteNoise ready
# ================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================
# Media files
# ================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ================================
# Default PK
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# Login redirects
# ================================
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
