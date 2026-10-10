# .k8s.settings.py — env-driven settings for containerised TLOJ.
#
# Commit this at the repo root, next to .ci.settings.py.
# The Dockerfile copies it into place:   COPY .k8s.settings.py dmoj/local_settings.py
#
# dmoj/settings.py exec()s this file inside its own namespace, so `os`, `BASE_DIR`
# and every default defined before the exec (MIDDLEWARE, STATICFILES_FINDERS, ...)
# are already in scope. That is why there are no imports and why `+=` works.
#
# RULES
#   1. No values live in this file. Anything environment-specific is an env var,
#      supplied by values.yaml (non-secret) or by the online-judge-secrets Secret (secret).
#   2. Anything constant across dev and prd IS hardcoded here — it is code.
#   3. Names use Cake's double-underscore convention (MYSQL__HOST, EVENT__KEY).
#
# DEPLOYMENT MODEL THIS FILE ASSUMES
#   Browser -> Cloudflare edge (TLS) -> cloudflared pod -> gunicorn (plain HTTP).
#   Django therefore never sees TLS or the client's IP directly; see the
#   "Behind Cloudflare Tunnel" section below.

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


ENV = _env('ENV', 'dev')                                    # dev | prd

# One hostname drives every URL-shaped setting below. Moving dev from
# oj-dev.tloi.vn to oj.dev.tloi.vn later is a one-line change in values.yaml.
_DOMAIN = _env('SITE__DOMAIN', 'localhost', required=True)  # e.g. oj-dev.tloi.vn


#####################################
########## Django settings ##########
#####################################

SECRET_KEY = _env('DJANGO__SECRET_KEY', 'build-only-not-a-real-key', required=True)
DEBUG = _env('DJANGO__DEBUG', False, cast=bool)
ALLOWED_HOSTS = _env('DJANGO__ALLOWED_HOSTS', [_DOMAIN], cast=list)

# Sign-up form on/off (values.yaml sets it false on dev).
REGISTRATION_OPEN = _env('DJANGO__REGISTRATION_OPEN', True, cast=bool)

INSTALLED_APPS += (
)


#########################################
########## Behind Cloudflare Tunnel #####
#########################################
# Three things that break SILENTLY if Django doesn't know it's behind a proxy.

# 1. HTTPS detection. TLS ends at Cloudflare; gunicorn sees plain HTTP.
#    Without this, request.is_secure() is False, so build_absolute_uri() emits
#    http:// URLs — Google OAuth rejects the redirect_uri, and Django 4's CSRF
#    origin check fails on every POST from an https:// page.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://%s' % _DOMAIN]
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# 2. Real client IP. gunicorn sets REMOTE_ADDR to the cloudflared pod, and DMOJ
#    reads REMOTE_ADDR directly (judge/user_log.py, the password-reset throttle in
#    judge/views/user.py, IP_BASED_AUTHENTICATION_HEADER). Without this, every
#    visitor is one IP: one person's reset attempts throttle everyone, and contest
#    IP logs become useless. See dmoj/cf_realip.py for the trust model.
#
# 3. Static files. No host nginx in front any more, so WhiteNoise serves
#    /static/ from inside gunicorn (Cloudflare caches it at the edge).
#    Order matters: real-IP first, WhiteNoise next, then DMOJ's own chain.
_PREPEND = ['whitenoise.middleware.WhiteNoiseMiddleware']
if _env('PROXY__CLOUDFLARE', True, cast=bool):
    _PREPEND.insert(0, 'dmoj.cf_realip.CloudflareRealIPMiddleware')
MIDDLEWARE = tuple(_PREPEND) + tuple(MIDDLEWARE)


##############################
########## Database ##########
##############################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': _env('MYSQL__DATABASE', 'dmoj'),
        'USER': _env('MYSQL__USER', 'dmoj'),
        'PASSWORD': _env('MYSQL__PASSWORD', ''),
        'HOST': _env('MYSQL__HOST', '127.0.0.1'),
        'PORT': _env('MYSQL__PORT', 3306, cast=int),
        'CONN_MAX_AGE': _env('MYSQL__CONN_MAX_AGE', 60, cast=int),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION',
        },
    },
}


###########################
########## Cache ##########
###########################
# WAS LocMemCache — per-process, so site and judge never shared a cache.
# Redis is mandatory once there is more than one process.

_redis_pw = _env('REDIS__PASSWORD', '')
_redis_auth = ':%s@' % _redis_pw if _redis_pw else ''
_redis_base = 'redis://%s%s:%s' % (_redis_auth,
                                   _env('REDIS__HOST', 'redis'),
                                   _env('REDIS__PORT', 6379, cast=int))

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '%s/%s' % (_redis_base, _env('REDIS__CACHE_DB', 1, cast=int)),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    },
}

CELERY_BROKER_URL = '%s/%s' % (_redis_base, _env('REDIS__CELERY_DB', 2, cast=int))
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

STATIC_ROOT = _env('STATIC__ROOT', os.path.join(BASE_DIR, 'static'))
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Files served at the site root (robots.txt, favicon.ico, the icon set) —
# what the upstream nginx config served via its @icons location. The image
# build copies them here.
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'rootfiles')

# User uploads. STATE — a PersistentVolume, never the container filesystem.
# Served by the online-judge-media nginx pod, not Django. MEDIA_URL is the site root, as
# in upstream VNOJ: uploads live at /martor/, /pdf/, /submission_file/ and
# /static-upload/ (see *_UPLOAD_URL_PREFIX in dmoj/settings.py), and those URLs
# are already embedded in problem statements stored in the database.
MEDIA_ROOT = _env('MEDIA__ROOT', '/media')
MEDIA_URL = _env('MEDIA__URL', '/')

# django-compressor is DISABLED: {% compress %} blocks render their contents
# unchanged and WhiteNoise serves the individual files.
#  - Offline compression can't work here: the compress blocks in base.html and
#    friends depend on request context (inlinei18n(LANGUAGE_CODE), theme
#    variables), so the offline manifest never matches at render time.
#  - Online compression (what upstream VNOJ does) writes bundles into
#    STATIC_ROOT at request time, which needs a shared writable volume plus
#    nginx to serve it. WhiteNoise only serves files that exist at startup.
# Behind Cloudflare (HTTP/2 + edge caching + compression) the extra requests are
# cheap. Re-enabling means a shared static volume — see the dev plan.
COMPRESS_ENABLED = False


#########################################
########## Email configuration ##########
#########################################
# WAS localhost:25 — there is no MTA in a container.

EMAIL_BACKEND = _env('MAIL__BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = _env('MAIL__HOST', 'localhost')
EMAIL_PORT = _env('MAIL__PORT', 25, cast=int)
EMAIL_USE_TLS = _env('MAIL__USE_TLS', False, cast=bool)
EMAIL_HOST_USER = _env('MAIL__USER', '')
EMAIL_HOST_PASSWORD = _env('MAIL__PASSWORD', '')

DEFAULT_FROM_EMAIL = _env('MAIL__FROM', 'TLOI Support <support@tloi.vn>')
SERVER_EMAIL = _env('MAIL__SERVER_EMAIL', 'support@tloi.vn')

# MAIL__ADMINS format: "name:email,name:email"
ADMINS = tuple(
    tuple(pair.split(':', 1))
    for pair in _env('MAIL__ADMINS', [], cast=list)
    if ':' in pair
)


############################################
########## DMOJ-specific settings ##########
############################################

SITE_NAME = _env('SITE__NAME', 'TLOJ')
SITE_FULL_URL = 'https://%s' % _DOMAIN
SITE_LONG_NAME = 'TLOJ: Thang Long Da Lat Online Judge'
SITE_ADMIN_EMAIL = _env('SITE__ADMIN_EMAIL', 'support@tloi.vn')
TERMS_OF_SERVICE_URL = '//%s/tos/' % _DOMAIN

# Site side of problem data (admin test-data editor writes here).
# The judge has its own read-only copy — see the dev plan, problem data section.
DMOJ_PROBLEM_DATA_ROOT = _env('PROBLEM__DATA_ROOT', '/problems')

## Bridge.
# The bridge pod BINDS 0.0.0.0 (not localhost, or nothing outside the pod can
# reach it). Site/celery pods CONNECT to it through its ClusterIP Service.
# Judges are in-cluster, so neither port is ever exposed outside the cluster.
BRIDGED_JUDGE_ADDRESS = [(_env('BRIDGE__JUDGE_HOST', '0.0.0.0'),
                          _env('BRIDGE__JUDGE_PORT', 9999, cast=int))]
BRIDGED_DJANGO_ADDRESS = [(_env('BRIDGE__DJANGO_HOST', '0.0.0.0'),
                           _env('BRIDGE__DJANGO_PORT', 9998, cast=int))]
BRIDGED_DJANGO_CONNECT = (_env('BRIDGE__CONNECT_HOST', 'online-judge-bridge'),
                          _env('BRIDGE__DJANGO_PORT', 9998, cast=int))

## DMOJ features.
ENABLE_FTS = _env('FEATURE__ENABLE_FTS', False, cast=bool)
BAD_MAIL_PROVIDERS = set()

## Event server (websocket/daemon.js). Ports follow the DMOJ standard:
## 15100 = websocket GET (browsers), 15101 = POST (site), 15102 = HTTP long-poll.
EVENT_DAEMON_USE = _env('EVENT__USE', True, cast=bool)
EVENT_DAEMON_POST = _env('EVENT__POST', 'ws://online-judge-wsevent:15101/')
EVENT_DAEMON_GET = 'ws://%s/event/' % _DOMAIN
EVENT_DAEMON_GET_SSL = 'wss://%s/event/' % _DOMAIN
EVENT_DAEMON_POLL = '/channels/'
# VNOJ's websocket/daemon.js has no `auth` command: with any key set, the site
# sends one, the daemon answers "bad-command" and every page 500s. The POST
# port (15101) is cluster-internal only (no tunnel route; the judge's
# NetworkPolicy blocks it), so no key is needed.
EVENT_DAEMON_KEY = None

# Never overridden before, so the site ran on the public literals hardcoded in
# dmoj/settings.py. Required here: a pod without them refuses to start.
EVENT_DAEMON_SUBMISSION_KEY = _env('EVENT__SUBMISSION_KEY', 'build-only', required=True)
EVENT_DAEMON_CONTEST_KEY = _env('EVENT__CONTEST_KEY', 'build-only', required=True)
EVENT_DAEMON_TICKET_KEY = _env('EVENT__TICKET_KEY', 'build-only', required=True)


#############################
########## Logging ##########
#############################
# WAS a RotatingFileHandler writing bridge_log.txt into the working directory.
# In a pod that's invisible and lost on every roll. Everything goes to stdout.

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
        'judge.bridge': {'handlers': ['console', 'mail_admins'], 'level': _env('LOG__LEVEL', 'INFO'),
                         'propagate': True},
        '': {'handlers': ['console'], 'level': _env('LOG__LEVEL', 'INFO')},
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
# Add https://<SITE__DOMAIN>/complete/google-oauth2/ to the OAuth client's
# authorised redirect URIs for every environment that uses it.

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = _env('SOCIAL__GOOGLE_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = _env('SOCIAL__GOOGLE_SECRET', '')


########################################
########## Custom configuration ########
########################################

GROUP_PERMISSION_FOR_ORG_ADMIN = 'Teacher'
VNOJ_CONTEST_DURATION_LIMIT = 365
