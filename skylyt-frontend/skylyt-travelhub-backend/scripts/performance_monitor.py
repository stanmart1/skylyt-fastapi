#!/usr/bin/env python3
"""
Performance monitoring script for Skylyt TravelHub
"""
import sys
import os
import time
import psutil
import requests
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.utils.logger import get_logger
from app.utils.query_optimizer import DatabaseMonitor

logger = get_logger(__name__)

class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
    
    def check_system_resources(self) -> dict:
        """Check system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    
    def check_database_performance(self) -> dict:
        """Check database performance metrics"""
        try:
            db_stats = DatabaseMonitor.get_connection_stats(engine)
            
            # Test database response time
            start_time = time.time()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            db_response_time = time.time() - start_time
            
            db_stats["response_time"] = db_response_time
            return db_stats
            
        except Exception as e:
            logger.error(f"Database performance check failed: {e}")
            return {"error": str(e)}
    
    def check_api_performance(self) -> dict:
        """Check API endpoint performance"""
        endpoints = [
            "/api/v1/health",
            "/api/v1/health/detailed"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                }
                
            except Exception as e:
                results[endpoint] = {
                    "error": str(e),
                    "success": False
                }
        
        return results
    
    def check_cache_performance(self) -> dict:
        """Check Redis cache performance"""
        try:
            import redis
            from app.core.config import settings
            
            redis_client = redis.from_url(settings.REDIS_URL)
            
            # Test cache response time
            start_time = time.time()
            redis_client.ping()
            cache_response_time = time.time() - start_time
            
            # Get cache info
            info = redis_client.info()
            
            return {
                "response_time": cache_response_time,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
            }
            
        except Exception as e:
            logger.error(f"Cache performance check failed: {e}")
            return {"error": str(e)}
    
    def generate_performance_report(self) -> dict:
        """Generate comprehensive performance report"""
        timestamp = datetime.now().isoformat()
        
        report = {
            "timestamp": timestamp,
            "system": self.check_system_resources(),
            "database": self.check_database_performance(),
            "api": self.check_api_performance(),
            "cache": self.check_cache_performance()
        }
        
        # Calculate overall health score
        health_score = self.calculate_health_score(report)
        report["health_score"] = health_score
        
        return report
    
    def calculate_health_score(self, report: dict) -> float:
        """Calculate overall system health score (0-100)"""
        score = 100.0
        
        # System resources (30% weight)
        system = report.get("system", {})
        if system.get("cpu_percent", 0) > 80:
            score -= 10
        if system.get("memory_percent", 0) > 85:
            score -= 10
        if system.get("disk_percent", 0) > 90:
            score -= 10
        
        # Database performance (30% weight)
        database = report.get("database", {})
        if database.get("response_time", 0) > 1.0:
            score -= 15
        if database.get("error"):
            score -= 15
        
        # API performance (25% weight)
        api = report.get("api", {})
        failed_endpoints = sum(1 for endpoint in api.values() if not endpoint.get("success", False))
        score -= failed_endpoints * 12.5
        
        # Cache performance (15% weight)
        cache = report.get("cache", {})
        if cache.get("response_time", 0) > 0.1:
            score -= 5
        if cache.get("hit_rate", 1.0) < 0.5:
            score -= 10
        
        return max(0.0, score)

def main():
    """Main monitoring function"""
    monitor = PerformanceMonitor()
    
    try:
        logger.info("Starting performance monitoring...")
        report = monitor.generate_performance_report()
        
        # Log summary
        health_score = report["health_score"]
        logger.info(f"System Health Score: {health_score:.1f}/100")
        
        if health_score >= 90:
            logger.info("System performance: EXCELLENT")
        elif health_score >= 75:
            logger.info("System performance: GOOD")
        elif health_score >= 60:
            logger.warning("System performance: FAIR")
        else:
            logger.error("System performance: POOR")
        
        # Log detailed metrics
        system = report["system"]
        logger.info(f"CPU: {system['cpu_percent']:.1f}%, Memory: {system['memory_percent']:.1f}%, Disk: {system['disk_percent']:.1f}%")
        
        database = report["database"]
        if not database.get("error"):
            logger.info(f"Database response time: {database['response_time']:.3f}s")
        
        cache = report["cache"]
        if not cache.get("error"):
            logger.info(f"Cache hit rate: {cache['hit_rate']:.2f}, Response time: {cache['response_time']:.3f}s")
        
        # Save report to file
        import json
        with open(f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("Performance monitoring completed")
        
    except Exception as e:
        logger.error(f"Performance monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()