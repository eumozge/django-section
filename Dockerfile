FROM python:3.12-slim

ENV APP_DIR=/usr/src/app/
WORKDIR ${APP_DIR}

RUN apt update -y && \
    apt install -y python3-dev \
    gcc \
    musl-dev \
    libpq-dev \
    nmap

RUN pip install poetry
COPY poetry.toml pyproject.toml poetry.lock ${APP_DIR}
RUN poetry install --no-cache --no-interaction --no-ansi --no-root -vvv

COPY . ${APP_DIR}

EXPOSE 8000
