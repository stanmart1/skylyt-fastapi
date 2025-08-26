from celery import Celery
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.models.user import User
from app.models.booking import Booking
from app.models.payment import Payment, PaymentProof
from app.tasks.email_tasks import celery_app
from app.utils.logger import get_logger
import os
import shutil

logger = get_logger(__name__)

@celery_app.task
def cleanup_expired_sessions():
    """Clean up expired user sessions from Redis"""
    try:
        from app.utils.cache import cache_manager
        
        # This would typically scan Redis for expired session keys
        # For now, we'll just log the cleanup
        logger.info("Session cleanup completed")
        return {"status": "completed"}
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")
        raise

@celery_app.task
def cleanup_old_payment_proofs():
    """Clean up old payment proof files"""
    try:
        db = next(get_db())
        
        # Find payment proofs older than 90 days for completed/failed payments
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        old_proofs = db.query(PaymentProof).join(Payment).filter(
            and_(
                PaymentProof.created_at < cutoff_date,
                or_(
                    Payment.status == "completed",
                    Payment.status == "failed"
                )
            )
        ).all()
        
        deleted_files = 0
        deleted_records = 0
        
        for proof in old_proofs:
            # Delete file if it exists
            if proof.file_path and os.path.exists(proof.file_path):
                try:
                    os.remove(proof.file_path)
                    deleted_files += 1
                except OSError:
                    pass
            
            # Delete database record
            db.delete(proof)
            deleted_records += 1
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_files} files and {deleted_records} payment proof records")
        return {
            "deleted_files": deleted_files,
            "deleted_records": deleted_records
        }
        
    except Exception as e:
        logger.error(f"Payment proof cleanup failed: {str(e)}")
        raise

@celery_app.task
def cleanup_cancelled_bookings():
    """Clean up old cancelled bookings"""
    try:
        db = next(get_db())
        
        # Find cancelled bookings older than 1 year
        cutoff_date = datetime.utcnow() - timedelta(days=365)
        
        old_bookings = db.query(Booking).filter(
            and_(
                Booking.status == "cancelled",
                Booking.cancelled_at < cutoff_date
            )
        ).all()
        
        deleted_count = 0
        for booking in old_bookings:
            db.delete(booking)
            deleted_count += 1
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old cancelled bookings")
        return {"deleted_bookings": deleted_count}
        
    except Exception as e:
        logger.error(f"Cancelled bookings cleanup failed: {str(e)}")
        raise

@celery_app.task
def cleanup_unverified_users():
    """Clean up unverified user accounts older than 7 days"""
    try:
        db = next(get_db())
        
        # Find unverified users older than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        unverified_users = db.query(User).filter(
            and_(
                User.is_verified == False,
                User.created_at < cutoff_date
            )
        ).all()
        
        deleted_count = 0
        for user in unverified_users:
            # Check if user has any bookings
            has_bookings = db.query(Booking).filter(Booking.user_id == user.id).first()
            
            if not has_bookings:
                db.delete(user)
                deleted_count += 1
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} unverified user accounts")
        return {"deleted_users": deleted_count}
        
    except Exception as e:
        logger.error(f"Unverified users cleanup failed: {str(e)}")
        raise

@celery_app.task
def cleanup_temp_files():
    """Clean up temporary files"""
    try:
        temp_dirs = [
            "/tmp/skylyt_uploads",
            "uploads/temp"
        ]
        
        deleted_files = 0
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_time < cutoff_time:
                            try:
                                os.remove(file_path)
                                deleted_files += 1
                            except OSError:
                                pass
        
        logger.info(f"Cleaned up {deleted_files} temporary files")
        return {"deleted_files": deleted_files}
        
    except Exception as e:
        logger.error(f"Temp files cleanup failed: {str(e)}")
        raise

@celery_app.task
def cleanup_old_logs():
    """Clean up old log files"""
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return {"status": "no_logs_directory"}
        
        cutoff_date = datetime.now() - timedelta(days=30)
        deleted_files = 0
        
        for filename in os.listdir(log_dir):
            if filename.endswith('.log') and not filename.startswith('app.log'):
                file_path = os.path.join(log_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_files += 1
                    except OSError:
                        pass
        
        logger.info(f"Cleaned up {deleted_files} old log files")
        return {"deleted_files": deleted_files}
        
    except Exception as e:
        logger.error(f"Log cleanup failed: {str(e)}")
        raise

@celery_app.task
def database_maintenance():
    """Perform database maintenance tasks"""
    try:
        db = next(get_db())
        
        # Update statistics (PostgreSQL specific)
        db.execute("ANALYZE;")
        
        # Clean up any orphaned records
        # This is a placeholder - implement based on your specific needs
        
        db.commit()
        
        logger.info("Database maintenance completed")
        return {"status": "completed"}
        
    except Exception as e:
        logger.error(f"Database maintenance failed: {str(e)}")
        raise

# Periodic task to run all cleanup tasks
@celery_app.task
def run_daily_cleanup():
    """Run all daily cleanup tasks"""
    try:
        results = {}
        
        # Run cleanup tasks
        results["sessions"] = cleanup_expired_sessions.delay().get()
        results["payment_proofs"] = cleanup_old_payment_proofs.delay().get()
        results["temp_files"] = cleanup_temp_files.delay().get()
        results["logs"] = cleanup_old_logs.delay().get()
        
        logger.info(f"Daily cleanup completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Daily cleanup failed: {str(e)}")
        raise

@celery_app.task
def run_weekly_cleanup():
    """Run weekly cleanup tasks"""
    try:
        results = {}
        
        # Run weekly cleanup tasks
        results["cancelled_bookings"] = cleanup_cancelled_bookings.delay().get()
        results["unverified_users"] = cleanup_unverified_users.delay().get()
        results["database_maintenance"] = database_maintenance.delay().get()
        
        logger.info(f"Weekly cleanup completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Weekly cleanup failed: {str(e)}")
        raise