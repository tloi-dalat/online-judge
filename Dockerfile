# syntax=docker/dockerfile:1
#
# TLOJ site image. One image, four roles, selected by the command the chart sets:
#   site     gunicorn dmoj.wsgi:application   (default CMD)
#   bridge   python manage.py runbridged
#   celery   celery -A dmoj_celery worker
#   migrate  python manage.py migrate         (ArgoCD PreSync Job)
#
# Build context: the repo root WITH submodules checked out (resources/libs,
# resources/vnoj). In CI that's actions/checkout with `submodules: recursive`.
#
# Everything update_tloj.sh used to do on the VPS at deploy time happens here at
# build time, except `migrate`, which needs the database.

ARG PYTHON_IMAGE=python:3.12-slim-bookworm
ARG NODE_IMAGE=node:24-bookworm-slim

############################################################
# 1. Stylesheets: make_style.sh (sass + postcss)
############################################################
FROM ${NODE_IMAGE} AS assets
WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY make_style.sh ./
COPY scripts ./scripts
COPY resources ./resources
RUN ./make_style.sh

############################################################
# 2. Python dependencies, built into a venv
############################################################
FROM ${PYTHON_IMAGE} AS python-deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential pkg-config default-libmysqlclient-dev git \
 && rm -rf /var/lib/apt/lists/*
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH
COPY requirements.txt additional_requirements.txt requirements.k8s.txt ./
RUN pip install -r requirements.txt -r additional_requirements.txt -r requirements.k8s.txt

############################################################
# 3. Collect static files and compile translations
############################################################
FROM ${PYTHON_IMAGE} AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends gettext libmariadb3 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=python-deps /venv /venv
ENV PATH=/venv/bin:$PATH
WORKDIR /app
COPY . .
COPY --from=assets /src/resources ./resources
COPY .k8s.settings.py dmoj/local_settings.py
# BUILD_MODE lets the settings load without secrets or a database.
# Same order as update_tloj.sh.
RUN export BUILD_MODE=1 \
 && python manage.py collectstatic --noinput \
 && python manage.py compilemessages \
 && python manage.py compilejsi18n \
 && mkdir -p rootfiles \
 && cp resources/icons/* robots.txt rootfiles/

############################################################
# 4. Runtime
############################################################
FROM ${PYTHON_IMAGE}
# libmariadb3: mysqlclient at runtime. pandoc: Codeforces Polygon import
# (judge/utils/codeforces_polygon.py), which can also run inside celery.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libmariadb3 pandoc \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /venv /venv
COPY --from=build /app /app
WORKDIR /app
# The pod may run as any UID (it must match the owner of the media/problem
# directories on the host), so nothing here assumes a particular user exists.
# DJANGO_SETTINGS_MODULE is load-bearing: dmoj/__init__.py imports the Celery
# app, which reads settings before dmoj/wsgi.py gets to set it, so gunicorn
# fails to boot without it.
ENV PATH=/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=dmoj.settings \
    HOME=/tmp \
    MPLCONFIGDIR=/tmp/matplotlib
USER 1000:1000
EXPOSE 8000
CMD ["gunicorn", "dmoj.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--max-requests", "1000", "--max-requests-jitter", "100", \
     "--access-logfile", "-"]
