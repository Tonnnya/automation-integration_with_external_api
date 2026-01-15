# automation-integration_with_external_api

### Крок 1:

```bash
git clone <your-repo-url>
cd celery-fastapi-project
```

### Крок 2:
Файл `.env` :

```bash
# .env
REDIS_HOST=redis
REDIS_PORT=6379
API_URL=https://jsonplaceholder.typicode.com/users
CSV_OUTPUT_PATH=/app/data/users.csv
```

### Крок 3: 

```bash
docker-compose up --build

# Або в фоновому режимі:
docker-compose up -d --build
```

**Це запустить:**
- ✅ Redis (порт 6379)
- ✅ FastAPI (порт 8000)
- ✅ Celery Worker

### Крок 4:

```bash
# Перевірка API
curl http://localhost:8000/health

# Перевірка Celery
curl http://localhost:8000/ping-celery
```

### Крок 5: Відкрити інтерфейси

- **FastAPI Swagger**: http://localhost:8000/docs

## 🌐 API Ендпоінти

### GET `/`
Інформація про API

```bash
curl http://localhost:8000/
```

### GET `/health`
Перевірка здоров'я сервісу

```bash
curl http://localhost:8000/health
```

### POST `/fetch-users`
**Запустити задачу отримання користувачів вручну**

```bash
curl -X POST http://localhost:8000/fetch-users
```

**Відповідь:**
```json
{
  "task_id": "abc123...",
  "status": "pending",
  "message": "Task is in progress..."
}
```

### GET `/task/{task_id}`
**Перевірити статус виконання задачі**

```bash
curl http://localhost:8000/task/abc123...
```

**Відповідь (виконується):**
```json
{
  "task_id": "abc123...",
  "status": "PENDING",
  "result": null
}
```

**Відповідь (завершено):**
```json
{
  "task_id": "abc123...",
  "status": "SUCCESS",
  "result": {
    "status": "success",
    "users_count": 10,
    "csv_path": "/app/data/users.csv",
    "timestamp": "2026-01-13T12:00:00"
  }
}
```

### GET `/download-csv`
**Завантажити згенерований CSV файл**

```bash
curl http://localhost:8000/download-csv -o users.csv
```

### GET `/ping-celery`
**Перевірити з'єднання з Celery**

```bash
curl http://localhost:8000/ping-celery
```
