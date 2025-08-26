#!/usr/bin/env python3
"""
Database optimization script for Skylyt TravelHub
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.core.database import engine, SessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)

def analyze_table_statistics():
    """Analyze table statistics for optimization"""
    with engine.connect() as conn:
        if "postgresql" in str(engine.url):
            # PostgreSQL specific optimizations
            logger.info("Running PostgreSQL ANALYZE...")
            conn.execute(text("ANALYZE;"))
            
            # Update table statistics
            tables = ['users', 'bookings', 'payments', 'roles', 'permissions']
            for table in tables:
                conn.execute(text(f"ANALYZE {table};"))
                logger.info(f"Analyzed table: {table}")
        
        elif "sqlite" in str(engine.url):
            # SQLite specific optimizations
            logger.info("Running SQLite ANALYZE...")
            conn.execute(text("ANALYZE;"))

def vacuum_database():
    """Vacuum database to reclaim space and optimize"""
    with engine.connect() as conn:
        if "postgresql" in str(engine.url):
            logger.info("Running PostgreSQL VACUUM...")
            conn.execute(text("VACUUM ANALYZE;"))
        
        elif "sqlite" in str(engine.url):
            logger.info("Running SQLite VACUUM...")
            conn.execute(text("VACUUM;"))

def check_index_usage():
    """Check index usage statistics"""
    with engine.connect() as conn:
        if "postgresql" in str(engine.url):
            # Check unused indexes
            query = text("""
                SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
                ORDER BY schemaname, tablename;
            """)
            
            result = conn.execute(query)
            unused_indexes = result.fetchall()
            
            if unused_indexes:
                logger.warning("Unused indexes found:")
                for row in unused_indexes:
                    logger.warning(f"  {row.schemaname}.{row.tablename}.{row.indexname}")
            else:
                logger.info("All indexes are being used")

def optimize_queries():
    """Run query optimization recommendations"""
    db = SessionLocal()
    try:
        # Check for missing indexes on foreign keys
        inspector = inspect(engine)
        
        for table_name in inspector.get_table_names():
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            
            # Get column names from indexes
            indexed_columns = set()
            for index in indexes:
                indexed_columns.update(index['column_names'])
            
            # Check if foreign key columns are indexed
            for fk in foreign_keys:
                for column in fk['constrained_columns']:
                    if column not in indexed_columns:
                        logger.warning(f"Missing index on foreign key: {table_name}.{column}")
    
    finally:
        db.close()

def check_connection_pool():
    """Check database connection pool status"""
    pool = engine.pool
    logger.info(f"Connection pool status:")
    logger.info(f"  Pool size: {pool.size()}")
    logger.info(f"  Checked in: {pool.checkedin()}")
    logger.info(f"  Checked out: {pool.checkedout()}")
    logger.info(f"  Overflow: {pool.overflow()}")

def main():
    """Main optimization function"""
    logger.info("Starting database optimization...")
    
    try:
        # Check connection pool
        check_connection_pool()
        
        # Analyze table statistics
        analyze_table_statistics()
        
        # Check index usage
        check_index_usage()
        
        # Run query optimization checks
        optimize_queries()
        
        # Vacuum database
        vacuum_database()
        
        logger.info("Database optimization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()