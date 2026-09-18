"""
Celery application configuration for async task processing.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "hr_ai_platform",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "services.tasks.resume_tasks",
        "services.tasks.analytics_tasks",
        "services.tasks.notification_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "services.tasks.resume_tasks.*": {"queue": "resume_processing"},
        "services.tasks.analytics_tasks.*": {"queue": "analytics"},
        "services.tasks.notification_tasks.*": {"queue": "notifications"},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=4,
    task_acks_late=True,
    worker_max_tasks_per_child=100,
    
    # Result backend
    result_expires=3600,
    result_compression="gzip",
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-old-tasks": {
            "task": "services.tasks.maintenance.cleanup_old_task_results",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        "retrain-role-predictor": {
            "task": "services.tasks.analytics_tasks.retrain_role_predictor",
            "schedule": crontab(hour=3, minute=0, day_of_week=1),  # Weekly on Monday
        },
        "generate-daily-analytics": {
            "task": "services.tasks.analytics_tasks.generate_daily_analytics",
            "schedule": crontab(hour=1, minute=0),  # Daily at 1 AM
        },
    },
    
    # Task retry policy
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)


@celery_app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery worker."""
    print(f"Request: {self.request!r}")


if __name__ == "__main__":
    celery_app.start()