import os
import dj_database_url
from pathlib import Path
import cloudinary
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
API_KEY = os.environ.get("INTERNAL_API_KEY", "")


ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [
    "https://entergym.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'AuthFit',
    'cloudinary',
    'cloudinary_storage',
]

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
ROOT_URLCONF = 'Fitness.urls'

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
    }
]
WSGI_APPLICATION = 'Fitness.wsgi.application'

cloudinary.config(
    cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
    api_key=os.environ['CLOUDINARY_API_KEY'],
    api_secret=os.environ['CLOUDINARY_API_SECRET'],
)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ✅ Database
DATABASES = {
    'default': dj_database_url.parse(os.environ['DATABASE_URL'])
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_build")

# ✅ Redis — auto detects local vs cloud
REDIS_URL = os.environ['REDIS_URL']

# ✅ Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            **({"CONNECTION_POOL_KWARGS": {"ssl_cert_reqs": None}}
               if REDIS_URL.startswith('rediss://') else {})
        }
    }
}

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


JAZZMIN_SETTINGS = {
    "site_title": "EnterGYM Admin",
    "site_header": "EnterGYM Dashboard",
    "site_brand": "EnterGYM",
    "welcome_sign": "Welcome to EnterGYM Control Panel",
    "site_logo": "images/Logo.png",
    "site_icon": "images/Logo.png",
    "copyright": "EnterGYM",

    # 🔝 Top Menu
    "topmenu_links": [
        {"name": "Support", "url": "https://wa.me/917000032565", "new_window": True},
    ],

    # 👤 User menu
    "usermenu_links": [
        {"name": "Support", "url": "https://wa.me/917000032565", "new_window": True},
    ],

    # 📊 Sidebar
    "show_sidebar": True,
    "navigation_expanded": True,

    # 🎯 Order your apps (important for clean UI)
    "order_with_respect_to": [
        "AuthFit",
        "AuthFit.enrollment",
        "AuthFit.attendance",
        "AuthFit.membershipplan",
        "AuthFit.trainer",
        "AuthFit.contact",
        "AuthFit.gymnotification",
        "auth",
    ],

    # 🎨 Icons (VERY IMPORTANT for modern UI)
    "icons": {
        "AuthFit": "fas fa-dumbbell",

        "AuthFit.attendence": "fas fa-clipboard-user",
        "AuthFit.contact": "fas fa-address-book",
        "AuthFit.enrollment": "fas fa-id-card",
        "AuthFit.gymnotification": "fas fa-bell",
        "AuthFit.membershipplan": "fas fa-layer-group",
        "AuthFit.trainer": "fas fa-user-tie",

        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
    },

    # ⚡ UI Enhancements
    "changeform_format": "horizontal_tabs",
    "related_modal_active": False,

    # 🎨 Custom Styling
    "custom_css": "css/admin_custom.css",
    "custom_links": {
    "EnterGYM": [
        {
            "name": "Visit Website",
            "url": "https://entergym.onrender.com/",
            "icon": "fas fa-globe",
            "new_window": True,
        },
        {
            "name": "Support",
            "url": "https://wa.me/917000032565",
            "icon": "fas fa-headset",
            "new_window": True
        }
        ]
    }
}