# Notification Service

Сервис для асинхронной отправки уведомлений через email, Telegram и SMS.

Реальная отправка уведомлений не выполняется. Вместо этого Celery worker имитирует отправку через логирование, а затем обновляет статус уведомления в базе данных.

## Стек

- Python 3.12
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Redis
- Celery
- Pydantic
- Docker Compose
- Pytest

## Архитектура

```text
Client
  |
  v
Flask API
  |
  |-- создаёт уведомление в PostgreSQL со статусом queued
  |
  |-- кладёт задачу в Redis broker
                  |
                  v
            Celery worker
                  |
                  |-- имитирует отправку
                  |
                  v
            обновляет статус в PostgreSQL
```

Статусы уведомления:

```text
queued  -> уведомление создано и поставлено в очередь
pending -> worker начал обработку
sent    -> отправка успешно сымитирована
failed  -> во время обработки произошла ошибка
```

## Запуск через Docker

### 1. Склонировать репозиторий

```bash
git clone https://github.com/kristinabykova/notification-service.git
cd notification-service
```

### 2. Создать `.env`

```bash
cp .env.example .env
```

### 3. Запустить сервис

```bash
docker compose up --build
```


## Примеры запросов

### Создать email-уведомление

```bash
curl -X POST http://127.0.0.1:5000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "recipient": "user@example.com",
    "subject": "Test email",
    "message": "Hello from notification service"
  }'
```

Ожидаемый ответ:

```json
{
  "id": "f5561f47-db84-4bdf-b6aa-4b4192e911bf",
  "status": "queued"
}
```


### Создать SMS-уведомление

```bash
curl -X POST http://127.0.0.1:5000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sms",
    "recipient": "+79991234567",
    "message": "Your code is 1234"
  }'
```

Ожидаемый ответ:

```json
{
  "id": "2a6f7d23-d731-45c9-a4fb-b5fb7b05cc32",
  "status": "queued"
}
```



### Создать Telegram-уведомление

```bash
curl -X POST http://127.0.0.1:5000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "telegram",
    "recipient": "@test_user",
    "message": "Hello telegram"
  }'
```

Ожидаемый ответ:

```json
{
  "id": "7e48f58c-4b55-48f5-a2c6-3f3d2d25e60b",
  "status": "queued"
}
```



### Получить уведомление по id

```bash
curl http://127.0.0.1:5000/api/v1/notifications/f5561f47-db84-4bdf-b6aa-4b4192e911bf
```

Ожидаемый ответ после обработки worker-ом:

```json
{
  "id": "f5561f47-db84-4bdf-b6aa-4b4192e911bf",
  "status": "sent",
  "error": null
}
```



### Получить список всех уведомлений

```bash
curl http://127.0.0.1:5000/api/v1/notifications
```

Ожидаемый ответ:

```json
{
  "items": [
    {
      "id": "f5561f47-db84-4bdf-b6aa-4b4192e911bf",
      "status": "sent",
      "error": null
    }
  ]
}
```


### Получить уведомления по статусу

```bash
curl "http://127.0.0.1:5000/api/v1/notifications?status=sent"
```

Пример ответа:

```json
{
  "items": [
    {
      "id": "f5561f47-db84-4bdf-b6aa-4b4192e911bf",
      "status": "sent",
      "error": null
    }
  ]
}
```



### Получить уведомления с пагинацией

```bash
curl "http://127.0.0.1:5000/api/v1/notifications?limit=5&offset=0"
```

Пример ответа:

```json
{
  "items": [
    {
      "id": "f5561f47-db84-4bdf-b6aa-4b4192e911bf",
      "status": "sent",
      "error": null
    }
  ]
}
```



### Получить уведомления с фильтром и пагинацией

```bash
curl "http://127.0.0.1:5000/api/v1/notifications?status=sent&limit=5&offset=0"
```

Пример ответа:

```json
{
  "items": [
    {
      "id": "f5561f47-db84-4bdf-b6aa-4b4192e911bf",
      "status": "sent",
      "error": null
    }
  ]
}
```

## Проверка валидации

### Некорректный email

```bash
curl -X POST http://127.0.0.1:5000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "recipient": "wrong-email",
    "subject": "Bad email",
    "message": "Test"
  }'
```

Ожидаемый результат:

```text
HTTP 422
```

Уведомление при этом не создаётся, потому что ошибка произошла на этапе валидации входных данных.

## Проверка failed-статуса

Если отправить уведомление с текстом `"fail"`, worker специально сымитирует ошибку отправки.

```bash
curl -X POST http://127.0.0.1:5000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "recipient": "user@example.com",
    "subject": "Fail test",
    "message": "fail"
  }'
```

Ожидаемый ответ при создании:

```json
{
  "id": "9a87d79e-0dd1-4d48-9f95-186ed6b78f7b",
  "status": "queued"
}
```

После обработки запрос по id вернёт:

```bash
curl http://127.0.0.1:5000/api/v1/notifications/9a87d79e-0dd1-4d48-9f95-186ed6b78f7b
```

Ожидаемый ответ:

```json
{
  "id": "9a87d79e-0dd1-4d48-9f95-186ed6b78f7b",
  "status": "failed",
  "error": "Mock notification sending error"
}
```

## Тесты

Запустить тесты:

```bash
python -m pytest
```

