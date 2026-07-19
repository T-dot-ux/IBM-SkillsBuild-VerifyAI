import logging
import sys
import json
from datetime import datetime, timezone

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "agent": getattr(record, "agent_name", "System"),
            "message": record.getMessage()
        }
        
        # Add any extra attributes
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
        if hasattr(record, "action"):
            log_data["action"] = record.action
            
        return json.dumps(log_data)

def get_agent_logger(agent_name: str) -> logging.Logger:
    logger = logging.getLogger(f"verifyai.{agent_name}")
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        
    # Bind the agent name to the logger
    logger = logging.LoggerAdapter(logger, {"agent_name": agent_name})
    return logger
