import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# تحميل ملف .env
load_dotenv()

# ================================
# المسار الأساسي
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# مفاتيح النظام
# ================================
SECRET_KEY = os.getenv("SECRET_KEY", "DEVELOPMENT_ONLY_SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ================================
# التطبيقات
# ================================
INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project Apps
    'accounts_app.apps.AccountsAppConfig',
    'locations_app.apps.LocationsAppConfig',
    'assets_app.apps.AssetsAppConfig',
    'inventory_app.apps.InventoryAppConfig',
    'reports_app.apps.ReportsAppConfig',
]

# ================================
# Middleware + WhiteNoise
# ================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    # Arabic Support
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

                # Custom context processors
                'splasset.context_processors.user_groups',
                'splasset.context_processors.pending_sessions',
            ],
        },
    },
]

# ================================
# قاعدة البيانات — dev / production
# ================================

# 🔥 توليد DATABASE_URL من القيم المفصلة إن لم يكن موجودًا
if not os.getenv("DATABASE_URL"):
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")

    if db_host and db_name and db_user:
        os.environ["DATABASE_URL"] = (
            f"postgresql://{db_user}:{db_pass}"
            f"@{db_host}:{db_port}/{db_name}"
        )

# 🔥 إذا لم تتوفر DATABASE_URL → نستخدم SQLite تلقائيًا (للتطوير)
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=False if DEBUG else True
    )
}

# ================================
# Password Validators
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ================================
# لغة وتوقيت
# ================================
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# ================================
# Static files — WhiteNoise Ready
# ================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================
# Media
# ================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# ================================
# PK Default
# ================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# Redirects
# ================================
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
