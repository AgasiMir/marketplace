FROM python:3.12-slim

# Установка uv
RUN pip install uv

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей через uv
RUN uv sync --frozen

# Добавляем виртуальное окружение в PATH.
ENV PATH="/app/.venv/bin:$PATH"

# Копирование остальных файлов приложения
COPY . .
