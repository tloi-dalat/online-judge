# Settings for the container image, copied to dmoj/local_settings.py.
# Every environment variable has the name of the setting it sets.

from urllib.parse import urlsplit

_DISCORD_EVENTS = ('default', 'on_new_ticket', 'on_new_comment', 'on_new_problem', 'on_new_suggested_problem',
                   'on_new_tag_problem', 'on_new_tag', 'on_new_blogpost', 'on_error', 'on_long_queue',
                   'queue_time_stats')


def _env(key, default=None, required=False, cast=str):
    v = os.environ.get(key)
    if v is None or v == '':
        if required and not os.environ.get('BUILD_MODE'):
            raise RuntimeError('missing required environment variable: %s' % key)
        return default
    if cast is bool:
        return v.strip().lower() in ('1', 'true', 'yes', 'on')
    if cast is list:
        return [x.strip() for x in v.split(',') if x.strip()]
    return cast(v)


def _address(value):
    host, _, port = value.rpartition(':')
    return host, int(port)


SITE_FULL_URL = _env('SITE_FULL_URL', 'http://localhost', required=True).rstrip('/')
_DOMAIN = urlsplit(SITE_FULL_URL).hostname


#####################################
########## Django settings ##########
#####################################

SECRET_KEY = _env('SECRET_KEY', 'build-only-not-a-real-key', required=True)
# Encrypts with SECRET_KEY; FERNET_KEYS adds older keys so data encrypted with them stays readable.
FERNET_KEYS = [SECRET_KEY] + _env('FERNET_KEYS', [], cast=list)
DEBUG = _env('DEBUG', False, cast=bool)
ALLOWED_HOSTS = _env('ALLOWED_HOSTS', [_DOMAIN], cast=list)

REGISTRATION_OPEN = _env('REGISTRATION_OPEN', True, cast=bool)

INSTALLED_APPS += (
)


#########################################
########## Behind Cloudflare Tunnel #####
#########################################

# TLS ends at Cloudflare.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [SITE_FULL_URL]
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Real client IP from Cloudflare, then static files from WhiteNoise.
MIDDLEWARE = ('dmoj.cf_realip.CloudflareRealIPMiddleware',
              'whitenoise.middleware.WhiteNoiseMiddleware') + tuple(MIDDLEWARE)


##############################
########## Database ##########
##############################

# DATABASE_<KEY> sets DATABASES['default'][<KEY>].
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': _env('DATABASE_NAME', 'dmoj'),
        'USER': _env('DATABASE_USER', 'dmoj'),
        'PASSWORD': _env('DATABASE_PASSWORD', ''),
        'HOST': _env('DATABASE_HOST', '127.0.0.1'),
        'PORT': _env('DATABASE_PORT', 3306, cast=int),
        'CONN_MAX_AGE': _env('DATABASE_CONN_MAX_AGE', 60, cast=int),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION',
        },
    },
}


###########################
########## Cache ##########
###########################

# CACHES and the Celery broker share one Redis, on two database numbers.
_redis_pw = _env('REDIS_PASSWORD', '')
_redis_base = 'redis://%s%s:%s' % (':%s@' % _redis_pw if _redis_pw else '',
                                   _env('REDIS_HOST', 'redis'), _env('REDIS_PORT', 6379, cast=int))

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '%s/%s' % (_redis_base, _env('REDIS_CACHE_DB', 1, cast=int)),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    },
}

CELERY_BROKER_URL = '%s/%s' % (_redis_base, _env('REDIS_CELERY_DB', 2, cast=int))
CELERY_RESULT_BACKEND = CELERY_BROKER_URL


#############################################
########## Internationalization #############
#############################################

LANGUAGE_CODE = 'vi'
DEFAULT_USER_TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = True
USE_TZ = True


################################################
########## Static / media / compressor #########
################################################

STATIC_ROOT = _env('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Files served at the site root (robots.txt, favicon.ico, ...).
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'rootfiles')

# User uploads, served by the media pod.
MEDIA_ROOT = _env('MEDIA_ROOT', '/media')
MEDIA_URL = _env('MEDIA_URL', '/')

# Off: the compress blocks depend on request context.
COMPRESS_ENABLED = False


#########################################
########## Email configuration ##########
#########################################

EMAIL_BACKEND = _env('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = _env('EMAIL_HOST', 'localhost')
EMAIL_PORT = _env('EMAIL_PORT', 25, cast=int)
EMAIL_USE_TLS = _env('EMAIL_USE_TLS', False, cast=bool)
EMAIL_HOST_USER = _env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = _env('EMAIL_HOST_PASSWORD', '')
EMAIL_TIMEOUT = _env('EMAIL_TIMEOUT', 10, cast=int)

DEFAULT_FROM_EMAIL = _env('DEFAULT_FROM_EMAIL', 'TLOI Support <support@tloi.vn>')
SERVER_EMAIL = _env('SERVER_EMAIL', 'support@tloi.vn')

# name:email,name:email
ADMINS = tuple(tuple(pair.split(':', 1)) for pair in _env('ADMINS', [], cast=list) if ':' in pair)


############################################
########## DMOJ-specific settings ##########
############################################

SITE_NAME = _env('SITE_NAME', 'TLOJ')
SITE_LONG_NAME = _env('SITE_LONG_NAME', 'TLOJ: Thang Long Da Lat Online Judge')
SITE_ADMIN_EMAIL = _env('SITE_ADMIN_EMAIL', 'support@tloi.vn')
TERMS_OF_SERVICE_URL = '//%s/tos/' % _DOMAIN
DMOJ_CANONICAL = _env('DMOJ_CANONICAL', _DOMAIN)

DMOJ_PROBLEM_DATA_ROOT = _env('DMOJ_PROBLEM_DATA_ROOT', '/problems')

## Bridge: host:port, several separated by commas.
BRIDGED_JUDGE_ADDRESS = [_address(a) for a in _env('BRIDGED_JUDGE_ADDRESS', ['0.0.0.0:9999'], cast=list)]
BRIDGED_DJANGO_ADDRESS = [_address(a) for a in _env('BRIDGED_DJANGO_ADDRESS', ['0.0.0.0:9998'], cast=list)]
BRIDGED_DJANGO_CONNECT = _address(_env('BRIDGED_DJANGO_CONNECT', 'bridge:9998'))

## DMOJ features.
ENABLE_FTS = _env('ENABLE_FTS', False, cast=bool)
BAD_MAIL_PROVIDERS = set()

## Event server (websocket/daemon.js).
EVENT_DAEMON_USE = _env('EVENT_DAEMON_USE', True, cast=bool)
EVENT_DAEMON_POST = _env('EVENT_DAEMON_POST', 'ws://event:15101/')
EVENT_DAEMON_GET = 'ws://%s/event/' % _DOMAIN
EVENT_DAEMON_GET_SSL = 'wss://%s/event/' % _DOMAIN
EVENT_DAEMON_POLL = '/channels/'
# daemon.js has no auth command, so no key.
EVENT_DAEMON_KEY = None

EVENT_DAEMON_SUBMISSION_KEY = _env('EVENT_DAEMON_SUBMISSION_KEY', 'build-only', required=True)
EVENT_DAEMON_CONTEST_KEY = _env('EVENT_DAEMON_CONTEST_KEY', 'build-only', required=True)
EVENT_DAEMON_TICKET_KEY = _env('EVENT_DAEMON_TICKET_KEY', 'build-only', required=True)


#############################
########## Logging ##########
#############################

_LOG_LEVEL = _env('LOG_LEVEL', 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file': {'format': '%(levelname)s %(asctime)s %(module)s %(message)s'},
    },
    'handlers': {
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'file'},
        'mail_admins': {'level': 'ERROR', 'class': 'dmoj.throttle_mail.ThrottledEmailHandler'},
    },
    'loggers': {
        'django.request': {'handlers': ['mail_admins', 'console'], 'level': 'ERROR', 'propagate': False},
        'judge.bridge': {'handlers': ['console', 'mail_admins'], 'level': _LOG_LEVEL, 'propagate': True},
        '': {'handlers': ['console'], 'level': _LOG_LEVEL},
    },
}


#########################
########## CDN ##########
#########################

ACE_URL = '//cdnjs.cloudflare.com/ajax/libs/ace/1.2.3/'
JQUERY_JS = '//cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js'
SELECT2_JS_URL = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js'
SELECT2_CSS_URL = '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css'
TIMEZONE_MAP = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Blue_Marble_2002.png/1024px-Blue_Marble_2002.png'


##################################
########## Integrations ##########
##################################

# Redirect URI: <SITE_FULL_URL>/complete/google-oauth2/
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = _env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = _env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')


########################################
########## Custom configuration ########
########################################

GROUP_PERMISSION_FOR_ORG_ADMIN = 'Teacher'
VNOJ_CONTEST_DURATION_LIMIT = 365

# Log in with Google only.
OAUTH_ONLY = _env('OAUTH_ONLY', False, cast=bool)

# Codeforces Polygon import.
VNOJ_POLYGON_API_KEY = _env('VNOJ_POLYGON_API_KEY')
VNOJ_POLYGON_API_SECRET = _env('VNOJ_POLYGON_API_SECRET')
VNOJ_POLYGON_API_USERNAME = _env('VNOJ_POLYGON_API_USERNAME')

# MOSS plagiarism checks.
MOSS_API_KEY = _env('MOSS_API_KEY')

# DISCORD_WEBHOOK_<EVENT> sets DISCORD_WEBHOOK[<event>]; unset turns that notification off.
DISCORD_WEBHOOK = {event: _env('DISCORD_WEBHOOK_' + event.upper()) for event in _DISCORD_EVENTS}
DISCORD_WEBHOOK_PREFIX = _env('DISCORD_WEBHOOK_PREFIX', '')
if DISCORD_WEBHOOK['on_error']:
    LOGGING['handlers']['discord_webhook'] = {
        'level': 'ERROR', 'class': 'dmoj.throttle_discord_webhook.ThrottledDiscordWebhookHandler',
    }
    for _logger in ('django.request', 'judge.bridge'):
        LOGGING['loggers'][_logger]['handlers'].append('discord_webhook')

# Hide passwords in URLs and webhooks from error reports.
DEFAULT_EXCEPTION_REPORTER_FILTER = 'dmoj.safe_exception_reporter.SafeURLExceptionReporterFilter'
