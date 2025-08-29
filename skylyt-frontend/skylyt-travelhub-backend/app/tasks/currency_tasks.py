from celery import Celery
from app.core.database import SessionLocal
from app.services.currency_service import CurrencyService
import logging

logger = logging.getLogger(__name__)

def update_currency_rates():
    """Background task to update currency exchange rates"""
    db = SessionLocal()
    try:
        logger.info("Starting currency rate update...")
        CurrencyService.update_exchange_rates(db)
        logger.info("Currency rates updated successfully")
    except Exception as e:
        logger.error(f"Failed to update currency rates: {e}")
    finally:
        db.close()

# Schedule this task to run every hour
# In production, configure with: celery -A app.tasks.currency_tasks beat --loglevel=info