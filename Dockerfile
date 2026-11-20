ARG PYTHON_IMAGE=python:3.14-slim-trixie
ARG NODE_IMAGE=node:26-trixie-slim

# Stylesheets: make_style.sh (sass + postcss)
FROM ${NODE_IMAGE} AS assets
WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY make_style.sh ./
COPY scripts ./scripts
COPY resources ./resources
RUN ./make_style.sh

# Python dependencies, built into a venv
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

# Collect static files and compile translations
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
RUN export BUILD_MODE=1 \
 && python manage.py collectstatic --noinput \
 && python manage.py compilemessages \
 && python manage.py compilejsi18n \
 && mkdir -p rootfiles \
 && cp resources/icons/* robots.txt rootfiles/

# Runtime
FROM ${PYTHON_IMAGE}
RUN apt-get update \
 && apt-get install -y --no-install-recommends libmariadb3 pandoc \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /venv /venv
COPY --from=build /app /app
WORKDIR /app
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
