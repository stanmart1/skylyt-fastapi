import os
import logging
from typing import List, Dict
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class LogReader:
    def __init__(self):
        self.log_files = [
            "logs/app.log",
            "logs/error.log"
        ]
    
    def parse_log_line(self, line: str) -> Dict:
        """Parse log line to extract timestamp and message"""
        # Try to extract timestamp from log line
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}[.,]\d{3}[Z]?)'
        match = re.search(timestamp_pattern, line)
        
        if match:
            timestamp = match.group(1)
            # Clean up timestamp format
            timestamp = timestamp.replace(',', '.').replace(' ', 'T')
            if not timestamp.endswith('Z'):
                timestamp += 'Z'
        else:
            timestamp = datetime.now().isoformat() + 'Z'
        
        return {
            "timestamp": timestamp,
            "message": line.strip()
        }
    
    def get_recent_logs(self, lines: int = 100) -> List[Dict]:
        """Get recent logs from log files"""
        logs = []
        
        for log_file in self.log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        file_lines = f.readlines()
                        # Get last N lines
                        recent_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
                        
                        for line in recent_lines:
                            if line.strip():
                                parsed_log = self.parse_log_line(line)
                                parsed_log["source"] = log_file
                                logs.append(parsed_log)
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")
        
        # If no log files found, get recent logs from memory handler
        if not logs:
            logs = self.get_memory_logs(lines)
        
        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs[:lines]
    
    def get_memory_logs(self, lines: int = 50) -> List[Dict]:
        """Get logs from memory handler if available"""
        logs = []
        try:
            # Get root logger and check for handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers:
                if hasattr(handler, 'buffer'):
                    # Memory handler with buffer
                    for record in handler.buffer[-lines:]:
                        logs.append({
                            "timestamp": datetime.fromtimestamp(record.created).isoformat() + 'Z',
                            "message": f"{record.levelname} - {record.getMessage()}",
                            "source": "memory"
                        })
        except Exception as e:
            logger.error(f"Error getting memory logs: {e}")
        
        return logs

log_reader = LogReader()