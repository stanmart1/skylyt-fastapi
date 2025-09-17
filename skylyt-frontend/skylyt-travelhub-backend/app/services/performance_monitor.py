"""
Performance Monitoring Service
Monitors database performance, connection health, and system metrics
"""

import time
import psutil
import logging
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import engine, get_pool_status, check_database_health
from app.core.redis import get_redis, get_cache_stats
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system and database performance"""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            'db_response_time': 1.0,  # seconds
            'pool_utilization': 0.8,  # 80%
            'memory_usage': 0.85,     # 85%
            'cpu_usage': 0.80,        # 80%
            'cache_hit_rate': 0.70    # 70%
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_database_metrics(self, db: Session) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            start_time = time.time()
            
            # Test database connectivity
            db_health = check_database_health()
            
            # Get connection pool status
            pool_status = get_pool_status()
            
            # Get database statistics
            db_stats = self._get_database_stats(db)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'health': db_health,
                'pool': pool_status,
                'stats': db_stats,
                'response_time': response_time,
                'pool_utilization': pool_status['checked_out'] / pool_status['total_capacity'] if pool_status['total_capacity'] > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {'error': str(e)}
    
    def _get_database_stats(self, db: Session) -> Dict[str, Any]:
        """Get detailed database statistics"""
        try:
            # PostgreSQL specific queries
            queries = {
                'active_connections': "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'",
                'idle_connections': "SELECT count(*) FROM pg_stat_activity WHERE state = 'idle'",
                'database_size': "SELECT pg_size_pretty(pg_database_size(current_database()))",
                'table_stats': """
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
                    FROM pg_stat_user_tables 
                    WHERE schemaname = 'public'
                    ORDER BY n_live_tup DESC 
                    LIMIT 10
                """,
                'slow_queries': """
                    SELECT query, calls, total_time, mean_time, rows
                    FROM pg_stat_statements 
                    WHERE mean_time > 100 
                    ORDER BY mean_time DESC 
                    LIMIT 5
                """ if self._table_exists(db, 'pg_stat_statements') else None
            }
            
            stats = {}
            
            for key, query in queries.items():
                if query is None:
                    continue
                    
                try:
                    if key in ['active_connections', 'idle_connections']:
                        result = db.execute(text(query)).scalar()
                        stats[key] = result
                    elif key == 'database_size':
                        result = db.execute(text(query)).scalar()
                        stats[key] = result
                    elif key in ['table_stats', 'slow_queries']:
                        result = db.execute(text(query)).fetchall()
                        stats[key] = [dict(row._mapping) for row in result]
                except Exception as e:
                    logger.warning(f"Failed to get {key}: {e}")
                    stats[key] = None
            
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def _table_exists(self, db: Session, table_name: str) -> bool:
        """Check if a table exists"""
        try:
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = :table_name
                )
            """)
            result = db.execute(query, {"table_name": table_name}).scalar()
            return result
        except:
            return False
    
    def get_cache_metrics(self) -> Dict[str, Any]:
        """Get Redis/cache performance metrics"""
        try:
            redis_client = get_redis()
            if not redis_client:
                return {'status': 'unavailable'}
            
            # Get cache statistics
            cache_stats = get_cache_stats()
            
            # Test cache performance
            start_time = time.time()
            test_key = f"perf_test_{int(time.time())}"
            redis_client.set(test_key, "test", ex=10)
            redis_client.get(test_key)
            redis_client.delete(test_key)
            cache_response_time = time.time() - start_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'stats': cache_stats,
                'response_time': cache_response_time,
                'status': 'available'
            }
        except Exception as e:
            logger.error(f"Error getting cache metrics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_application_metrics(self, db: Session) -> Dict[str, Any]:
        """Get application-specific performance metrics"""
        try:
            # Count recent activities
            recent_queries = {
                'recent_bookings': "SELECT COUNT(*) FROM bookings WHERE created_at > NOW() - INTERVAL '1 hour'",
                'recent_payments': "SELECT COUNT(*) FROM payments WHERE created_at > NOW() - INTERVAL '1 hour'",
                'active_users': "SELECT COUNT(DISTINCT user_id) FROM bookings WHERE created_at > NOW() - INTERVAL '24 hours'",
                'pending_payments': "SELECT COUNT(*) FROM payments WHERE status = 'pending'",
                'failed_payments': "SELECT COUNT(*) FROM payments WHERE status = 'failed' AND created_at > NOW() - INTERVAL '24 hours'"
            }
            
            metrics = {}
            for key, query in recent_queries.items():
                try:
                    result = db.execute(text(query)).scalar()
                    metrics[key] = result or 0
                except Exception as e:
                    logger.warning(f"Failed to get {key}: {e}")
                    metrics[key] = 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {'metrics': {}}
    
    def check_performance_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance issues and generate alerts"""
        alerts = []
        
        try:
            # Check database response time
            if 'database' in metrics and 'response_time' in metrics['database']:
                if metrics['database']['response_time'] > self.alert_thresholds['db_response_time']:
                    alerts.append({
                        'type': 'database_slow',
                        'severity': 'warning',
                        'message': f"Database response time is {metrics['database']['response_time']:.2f}s",
                        'threshold': self.alert_thresholds['db_response_time']
                    })
            
            # Check pool utilization
            if 'database' in metrics and 'pool_utilization' in metrics['database']:
                if metrics['database']['pool_utilization'] > self.alert_thresholds['pool_utilization']:
                    alerts.append({
                        'type': 'pool_high_utilization',
                        'severity': 'warning',
                        'message': f"Database pool utilization is {metrics['database']['pool_utilization']:.1%}",
                        'threshold': self.alert_thresholds['pool_utilization']
                    })
            
            # Check memory usage
            if 'system' in metrics and 'memory' in metrics['system']:
                memory_percent = metrics['system']['memory']['percent'] / 100
                if memory_percent > self.alert_thresholds['memory_usage']:
                    alerts.append({
                        'type': 'high_memory_usage',
                        'severity': 'warning',
                        'message': f"Memory usage is {memory_percent:.1%}",
                        'threshold': self.alert_thresholds['memory_usage']
                    })
            
            # Check CPU usage
            if 'system' in metrics and 'cpu' in metrics['system']:
                cpu_percent = metrics['system']['cpu']['percent'] / 100
                if cpu_percent > self.alert_thresholds['cpu_usage']:
                    alerts.append({
                        'type': 'high_cpu_usage',
                        'severity': 'warning',
                        'message': f"CPU usage is {cpu_percent:.1%}",
                        'threshold': self.alert_thresholds['cpu_usage']
                    })
            
            # Check cache hit rate
            if 'cache' in metrics and 'stats' in metrics['cache'] and 'hit_rate' in metrics['cache']['stats']:
                hit_rate = metrics['cache']['stats']['hit_rate'] / 100
                if hit_rate < self.alert_thresholds['cache_hit_rate']:
                    alerts.append({
                        'type': 'low_cache_hit_rate',
                        'severity': 'info',
                        'message': f"Cache hit rate is {hit_rate:.1%}",
                        'threshold': self.alert_thresholds['cache_hit_rate']
                    })
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
        
        return alerts
    
    def get_comprehensive_metrics(self, db: Session) -> Dict[str, Any]:
        """Get all performance metrics in one call"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': self.get_system_metrics(),
                'database': self.get_database_metrics(db),
                'cache': self.get_cache_metrics(),
                'application': self.get_application_metrics(db)
            }
            
            # Check for alerts
            alerts = self.check_performance_alerts(metrics)
            metrics['alerts'] = alerts
            
            # Store in history (keep last 100 entries)
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting comprehensive metrics: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def get_performance_summary(self, db: Session) -> Dict[str, Any]:
        """Get a summary of current performance status"""
        try:
            metrics = self.get_comprehensive_metrics(db)
            
            # Calculate overall health score
            health_score = 100
            
            if 'database' in metrics and 'response_time' in metrics['database']:
                if metrics['database']['response_time'] > 2.0:
                    health_score -= 30
                elif metrics['database']['response_time'] > 1.0:
                    health_score -= 15
            
            if 'system' in metrics and 'memory' in metrics['system']:
                memory_percent = metrics['system']['memory']['percent']
                if memory_percent > 90:
                    health_score -= 25
                elif memory_percent > 80:
                    health_score -= 10
            
            if 'alerts' in metrics:
                health_score -= len(metrics['alerts']) * 5
            
            health_score = max(0, health_score)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'status': 'healthy' if health_score > 80 else 'warning' if health_score > 60 else 'critical',
                'alerts_count': len(metrics.get('alerts', [])),
                'database_response_time': metrics.get('database', {}).get('response_time', 0),
                'memory_usage': metrics.get('system', {}).get('memory', {}).get('percent', 0),
                'cpu_usage': metrics.get('system', {}).get('cpu', {}).get('percent', 0),
                'cache_status': metrics.get('cache', {}).get('status', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'health_score': 0,
                'status': 'error',
                'error': str(e)
            }

# Global instance
performance_monitor = PerformanceMonitor()