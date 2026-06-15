import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "run_id": getattr(record, "run_id", "N/A"),
            "product": getattr(record, "product", "N/A"),
            "week": getattr(record, "week", "N/A"),
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logger(name="pulse_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding multiple handlers if setup_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    return logger

def get_run_logger(run_id, product, week):
    logger = setup_logger()
    return logging.LoggerAdapter(logger, {"run_id": run_id, "product": product, "week": week})
