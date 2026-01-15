import os
from typing import Optional, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel

from app.config import settings

from celery.result import AsyncResult

from app.tasks import fetch_and_save_users
from app.celery_app import ping

app = FastAPI(
    title="User API",
    description="API for saving user information in csv"
)

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict] = None

@app.get("/")
def root():
    return {
        "message": "User API",
        "endpoints": {
            "GET /": "API info",
            "GET /health": "Service health monitoring",
            "POST /fetch-users": "Fetching users",
            "GET /task/{task_id}": "Status",
            "GET /download-csv": "Down csv",
            "GET /ping-celery": "Ping celery"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "redis": settings.redis_host,
        "celery_broker": settings.celery_broker_url
    }

@app.post("/fetch-users", response_model=TaskResponse)
def trigger_fetch_user():
    task = fetch_and_save_users.delay()
    return TaskResponse(
        task_id=task.id,
        status="pending",
        message="Task is in progress. Use the task_id to check the status"
    )

@app.get("/task/{task_id}", response_model=TaskStatusResponse)
def get_task_info(task_id: str):
    result = AsyncResult(task_id)
    return TaskStatusResponse(
        task_id=task_id,
        status=result.state,
        result=result.result if result.ready() else None
    )

@app.get("/download-csv")
def download_csv():
    csv_path = settings.csv_output_path

    if not os.path.exists(csv_path):
        raise HTTPException(
            status_code=404,
            detail="CSV file does not found. Use task /fetch-users"
        )

    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename="users.csv"
    )

@app.get("/ping-celery")
def ping_celery():
    try:
        result = ping.delay()
        response = result.get(timeout=5)

        return {
            "status": "success",
            "message": "Celery works",
            "response": response,
            "task_id": result.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error {str(e)}"
        )


