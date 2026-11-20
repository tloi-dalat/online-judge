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
        'NAME': 'ci',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': 13306,
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
}

DEFAULT_USER_TIME_ZONE = 'Asia/Ho_Chi_Minh'
VNOJ_ENABLE_SYNC_API = True
DMOJ_PROBLEM_DATA_ROOT = os.path.join(BASE_DIR, 'problem_data')


class _NoMigrations(dict):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = _NoMigrations()
