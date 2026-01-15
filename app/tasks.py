import csv
import logging
from datetime import datetime
from typing import List, Dict

from celery.result import AsyncResult


import httpx
import os

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(
    name="app.tasks.fetch_and_save_users",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)

def fetch_and_save_users(self) -> Dict[str, any]:
    try:
        logger.info("Fetching users from the API…")

        users = fetch_users_from_api()

        if not users:
            logger.warning("Empty list")
            return {
                "status": "warning",
                "message": "There are no users to save",
                "user_count": 0,
                "timestamp": datetime.now().isoformat()
            }

        logger.info(f"Len {len(users)} of users")

        save_users_to_csv(users)

        logger.info(f"Success! {len(users)} of users in csv")

        return {
            "status": "success",
            "message": f"Success. {len(users)} of users",
            "users_count": len(users),
            "csv_path": settings.csv_output_path,
            "timestamp": datetime.now().isoformat()
        }

    except httpx.HTTPError as e:
        logger.info(f"Error {e}")
        raise self.retry(e=e)

    except Exception as e:
        logger.error(f"Error {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

def fetch_users_from_api() -> List[Dict]:
    with httpx.Client(timeout=30.0) as client:
        response = client.get(settings.api_url)
        response.raise_for_status()

        users = response.json()

        filtered_users = [
            {
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email")
            }
            for user in users
        ]

        return filtered_users

def save_users_to_csv(users: List[Dict]) -> None:
    os.makedirs(os.path.dirname(settings.csv_output_path), exist_ok=True)

    with open(settings.csv_output_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'name', 'email']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for user in users:
            writer.writerow(user)

    logger.info(f"CSV saved: {settings.csv_output_path}")

@celery_app.task(name="app.tasks.get_task_status")
def get_task_status(task_id: str) -> Dict:
    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": result.state,
        "result": result.result if result.ready() else None,
    }


