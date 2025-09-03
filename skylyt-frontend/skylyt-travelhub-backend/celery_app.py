from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "skylyt_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.booking_tasks", 
        "app.tasks.cleanup_tasks",
        "app.tasks.payment_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "check-pending-bookings": {
        "task": "app.tasks.booking_tasks.check_pending_bookings",
        "schedule": 300.0,  # Every 5 minutes
    },
    "send-booking-reminders": {
        "task": "app.tasks.booking_tasks.send_booking_reminders", 
        "schedule": 3600.0,  # Every hour
    },
    "check-pending-payments": {
        "task": "app.tasks.payment_tasks.check_pending_payments",
        "schedule": 600.0,  # Every 10 minutes
    },
    "daily-cleanup": {
        "task": "app.tasks.cleanup_tasks.run_daily_cleanup",
        "schedule": 86400.0,  # Daily
    },
    "weekly-cleanup": {
        "task": "app.tasks.cleanup_tasks.run_weekly_cleanup",
        "schedule": 604800.0,  # Weekly
    },
    "generate-booking-reports": {
        "task": "app.tasks.booking_tasks.generate_booking_reports",
        "schedule": 86400.0,  # Daily
    },
}

if __name__ == "__main__":
    celery_app.start()