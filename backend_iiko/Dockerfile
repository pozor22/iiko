FROM python:3.13

RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock /temp/

WORKDIR /temp/

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY backend /backend

WORKDIR /backend

RUN adduser --disabled-password finance_app-user

USER finance_app-user

EXPOSE 8000