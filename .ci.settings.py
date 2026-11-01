COMPRESS_OUTPUT_DIR = 'cache'
STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dmoj',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': 13306,
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
}

# Model defaults read this (Profile.timezone) and migration 0220 froze
# 'Asia/Ho_Chi_Minh'. Without it CI falls back to settings.py's
# 'America/Toronto' and makemigrations --check reports a phantom migration.
DEFAULT_USER_TIME_ZONE = 'Asia/Ho_Chi_Minh'
VNOJ_ENABLE_SYNC_API = True
DMOJ_PROBLEM_DATA_ROOT = os.path.join(BASE_DIR, 'problem_data')
