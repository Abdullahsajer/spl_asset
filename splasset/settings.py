from pathlib import Path

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# مفتاح التشفير (غير مناسب للإنتاج)
SECRET_KEY = 'django-insecure-%lv-i2n6=!yge=!gt+p#b&5_r-taosrshffbee7d0c#_5h^o!7'

# وضع التطوير
DEBUG = True

# العناوين المسموح بها
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# التطبيقات المثبتة
INSTALLED_APPS = [
    # ⭐ تطبيقات Django الأساسية
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ⭐ تطبيقات المشروع
    'accounts_app.apps.AccountsAppConfig',
    'locations_app.apps.LocationsAppConfig',
    'assets_app.apps.AssetsAppConfig',
    'inventory_app.apps.InventoryAppConfig',
    'reports_app.apps.ReportsAppConfig',
]

# الوسائط الوسطية Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # ⭐ تفعيل دعم اللغة العربية RTL
    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# روابط المشروع
ROOT_URLCONF = 'splasset.urls'

# القوالب Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",   # ⭐ مجلد القوالب العام
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'splasset.wsgi.application'

# قاعدة البيانات — SQLite للتجربة
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# التحقق من كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ⭐ اللغة والزمن — الرياض
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# الملفات الثابتة Static Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# رفع الملفات Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# المعرّف الافتراضي
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# إعادة توجيه تسجيل الدخول
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'   
