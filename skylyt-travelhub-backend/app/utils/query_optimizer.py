from sqlalchemy.orm import Query, joinedload, selectinload
from sqlalchemy import text
from typing import List, Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_user_bookings_query(query: Query) -> Query:
        """Optimize user bookings query with eager loading"""
        return query.options(
            joinedload('payment'),
            selectinload('user')
        ).order_by(text('created_at DESC'))
    
    @staticmethod
    def optimize_booking_search_query(query: Query, filters: Dict[str, Any]) -> Query:
        """Optimize booking search with proper indexing"""
        # Use indexes for common filters
        if 'status' in filters:
            query = query.filter(text('status = :status')).params(status=filters['status'])
        
        if 'booking_type' in filters:
            query = query.filter(text('booking_type = :type')).params(type=filters['booking_type'])
        
        if 'date_from' in filters:
            query = query.filter(text('created_at >= :date_from')).params(date_from=filters['date_from'])
        
        return query.order_by(text('created_at DESC'))
    
    @staticmethod
    def optimize_payment_query(query: Query) -> Query:
        """Optimize payment queries"""
        return query.options(
            joinedload('booking').joinedload('user')
        ).order_by(text('created_at DESC'))
    
    @staticmethod
    def get_query_execution_plan(query: Query) -> str:
        """Get query execution plan for analysis"""
        try:
            compiled = query.statement.compile(compile_kwargs={"literal_binds": True})
            return str(compiled)
        except Exception as e:
            logger.error(f"Failed to get query plan: {e}")
            return "Unable to generate query plan"

class DatabaseMonitor:
    """Monitor database performance"""
    
    @staticmethod
    def log_slow_query(query_time: float, query: str, threshold: float = 1.0):
        """Log slow queries for optimization"""
        if query_time > threshold:
            logger.warning(f"Slow query detected: {query_time:.2f}s - {query[:200]}...")
    
    @staticmethod
    def get_connection_stats(engine) -> Dict[str, Any]:
        """Get database connection pool statistics"""
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }

# Query optimization decorators
def optimize_query(func):
    """Decorator to optimize database queries"""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        execution_time = time.time() - start_time
        DatabaseMonitor.log_slow_query(execution_time, func.__name__)
        
        return result
    return wrapper