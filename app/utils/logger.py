import json
import logging
import sys
from datetime import datetime, timezone

logger = logging.getLogger("notification_service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def log_event(event: str, **data):
    logger.info(
        json.dumps(
            {
                "time": datetime.now(timezone.utc).isoformat(),
                "event": event,
                **data,
            },
            ensure_ascii=False,
        )
    )
