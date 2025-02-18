# Используем базовый образ Python 3.13
FROM python:3.13

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы проекта
COPY pyproject.toml poetry.lock /temp/

# Устанавливаем рабочую директорию временно в /temp/
WORKDIR /temp/

# Устанавливаем зависимости через Poetry (под root)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Копируем исходный код приложения
COPY backend /backend

# Устанавливаем рабочую директорию
WORKDIR /backend

# Создаем пользователя для запуска приложения
RUN adduser --disabled-password finance_app-user

# Переключаемся на созданного пользователя
USER finance_app-user

# Открываем порт 8000
EXPOSE 8000
