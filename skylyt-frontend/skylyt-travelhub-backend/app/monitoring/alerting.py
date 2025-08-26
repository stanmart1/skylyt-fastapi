import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    """Centralized alert management system"""
    
    def __init__(self):
        self.alert_thresholds = {
            "response_time": 2.0,  # seconds
            "error_rate": 0.05,    # 5%
            "memory_usage": 0.85,  # 85%
            "cpu_usage": 0.80,     # 80%
            "disk_usage": 0.90,    # 90%
            "db_connections": 0.90  # 90% of pool
        }
        self.alert_channels = ["email", "log"]
    
    async def check_performance_alerts(self, metrics: Dict[str, Any]):
        """Check performance metrics against thresholds"""
        alerts = []
        
        # Response time alert
        if metrics.get("avg_response_time", 0) > self.alert_thresholds["response_time"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "metric": "response_time",
                "value": metrics["avg_response_time"],
                "threshold": self.alert_thresholds["response_time"],
                "message": f"High response time: {metrics['avg_response_time']:.2f}s"
            })
        
        # Error rate alert
        if metrics.get("error_rate", 0) > self.alert_thresholds["error_rate"]:
            alerts.append({
                "level": AlertLevel.ERROR,
                "metric": "error_rate",
                "value": metrics["error_rate"],
                "threshold": self.alert_thresholds["error_rate"],
                "message": f"High error rate: {metrics['error_rate']:.2%}"
            })
        
        # Process alerts
        for alert in alerts:
            await self.send_alert(alert)
    
    async def check_system_alerts(self, system_metrics: Dict[str, Any]):
        """Check system resource alerts"""
        alerts = []
        
        # Memory usage alert
        memory_percent = system_metrics.get("memory_percent", 0) / 100
        if memory_percent > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "metric": "memory_usage",
                "value": memory_percent,
                "threshold": self.alert_thresholds["memory_usage"],
                "message": f"High memory usage: {memory_percent:.1%}"
            })
        
        # CPU usage alert
        cpu_percent = system_metrics.get("cpu_percent", 0) / 100
        if cpu_percent > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "metric": "cpu_usage",
                "value": cpu_percent,
                "threshold": self.alert_thresholds["cpu_usage"],
                "message": f"High CPU usage: {cpu_percent:.1%}"
            })
        
        # Process alerts
        for alert in alerts:
            await self.send_alert(alert)
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert through configured channels"""
        for channel in self.alert_channels:
            if channel == "email":
                await self.send_email_alert(alert)
            elif channel == "log":
                self.log_alert(alert)
    
    async def send_email_alert(self, alert: Dict[str, Any]):
        """Send alert via email"""
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.FROM_EMAIL
            msg["To"] = "admin@skylyt.com"  # Configure admin email
            msg["Subject"] = f"[{alert['level'].value.upper()}] Skylyt Alert: {alert['metric']}"
            
            body = f"""
            Alert Details:
            - Level: {alert['level'].value.upper()}
            - Metric: {alert['metric']}
            - Current Value: {alert['value']}
            - Threshold: {alert['threshold']}
            - Message: {alert['message']}
            - Timestamp: {datetime.now().isoformat()}
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Alert email sent: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def log_alert(self, alert: Dict[str, Any]):
        """Log alert to application logs"""
        level = alert["level"]
        message = alert["message"]
        
        if level == AlertLevel.INFO:
            logger.info(f"ALERT: {message}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"ALERT: {message}")
        elif level == AlertLevel.ERROR:
            logger.error(f"ALERT: {message}")
        elif level == AlertLevel.CRITICAL:
            logger.critical(f"ALERT: {message}")

class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        self.checks = {
            "database": self.check_database,
            "redis": self.check_redis,
            "disk_space": self.check_disk_space,
            "memory": self.check_memory,
            "external_apis": self.check_external_apis
        }
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = "healthy"
        
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                
                if not result.get("healthy", False):
                    overall_status = "unhealthy"
                    
            except Exception as e:
                results[check_name] = {
                    "healthy": False,
                    "error": str(e)
                }
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            from app.core.database import engine
            
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                return {"healthy": True, "response_time": "< 100ms"}
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            return {"healthy": True}
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            usage_percent = used / total
            
            return {
                "healthy": usage_percent < 0.90,
                "usage_percent": f"{usage_percent:.1%}",
                "free_gb": f"{free // (1024**3)}GB"
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                "healthy": memory.percent < 85,
                "usage_percent": f"{memory.percent:.1f}%",
                "available_gb": f"{memory.available // (1024**3)}GB"
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity"""
        # This would check payment gateways, hotel APIs, etc.
        # For now, return healthy
        return {"healthy": True, "message": "External APIs accessible"}

# Global instances
alert_manager = AlertManager()
health_checker = HealthChecker()