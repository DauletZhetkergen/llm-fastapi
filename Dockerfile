# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY ./requirements.txt /app/requirements.txt
COPY ./app /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Открываем порт для FastAPI
EXPOSE 8000

# Команда запуска


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]