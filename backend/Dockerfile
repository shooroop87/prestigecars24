FROM python:3.11-slim

# Установка системных зависимостей (только для Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Сборка статики
RUN python manage.py collectstatic --noinput --clear

# Запуск
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]