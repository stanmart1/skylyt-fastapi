from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def execute_optimized_stats_query(db: Session, booking_type: str) -> Dict[str, Any]:
    """Execute optimized query for booking and payment statistics"""
    try:
        # Single query to get all stats at once
        query = text("""
            WITH booking_stats AS (
                SELECT 
                    COUNT(*) as total_bookings,
                    COUNT(CASE WHEN status IN ('confirmed', 'ongoing') THEN 1 END) as active_bookings
                FROM bookings 
                WHERE booking_type = :booking_type
            ),
            revenue_stats AS (
                SELECT 
                    COALESCE(SUM(CASE 
                        WHEN p.created_at >= CURRENT_DATE - INTERVAL '30 days' 
                        THEN p.amount ELSE 0 END), 0) as current_revenue,
                    COALESCE(SUM(CASE 
                        WHEN p.created_at >= CURRENT_DATE - INTERVAL '60 days' 
                        AND p.created_at < CURRENT_DATE - INTERVAL '30 days'
                        THEN p.amount ELSE 0 END), 0) as previous_revenue
                FROM payments p
                JOIN bookings b ON p.booking_id = b.id
                WHERE b.booking_type = :booking_type AND p.status = 'completed'
            )
            SELECT 
                bs.total_bookings,
                bs.active_bookings,
                rs.current_revenue,
                rs.previous_revenue,
                CASE 
                    WHEN rs.previous_revenue > 0 
                    THEN ROUND(((rs.current_revenue - rs.previous_revenue) / rs.previous_revenue * 100), 1)
                    ELSE 0 
                END as revenue_change
            FROM booking_stats bs, revenue_stats rs
        """)
        
        result = db.execute(query, {"booking_type": booking_type}).fetchone()
        
        if result:
            return {
                "total_bookings": result.total_bookings or 0,
                "active_bookings": result.active_bookings or 0,
                "current_revenue": float(result.current_revenue or 0),
                "revenue_change": float(result.revenue_change or 0)
            }
        
        return {
            "total_bookings": 0,
            "active_bookings": 0,
            "current_revenue": 0.0,
            "revenue_change": 0.0
        }
        
    except Exception as e:
        logger.error(f"Failed to execute optimized stats query: {e}")
        return {
            "total_bookings": 0,
            "active_bookings": 0,
            "current_revenue": 0.0,
            "revenue_change": 0.0
        }

def safe_db_operation(db: Session, operation_func, *args, **kwargs):
    """Safely execute database operation with proper rollback handling"""
    try:
        result = operation_func(db, *args, **kwargs)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Database operation failed: {e}")
        raise