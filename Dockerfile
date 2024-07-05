FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Открываем порт, который будет использовать наше приложение
EXPOSE 5000

CMD ["python", "HHru.py"]

