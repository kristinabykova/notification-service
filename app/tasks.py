import time
from uuid import UUID

from celery import Celery

from app.config import settings
from app.crud.notifications import get_notification_by_id, update_notification_status
from app.db.models import Notification, NotificationStatus
from app.factory import create_app
from app.utils.logger import log_event

celery_app = Celery(
    "notification_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

flask_app = create_app()


def imitate_send(notification: Notification) -> None:
    log_event(
        "notification_send_mock",
        notification_id=str(notification.id),
        type=notification.type,
        recipient=notification.recipient,
    )

    time.sleep(1)

    if notification.message.strip().lower() == "fail":
        raise RuntimeError("Mock notification sending error")


@celery_app.task(name="process_notification")
def process_notification(notification_id: str) -> None:
    with flask_app.app_context():
        try:
            notification = get_notification_by_id(UUID(notification_id))

            if notification is None:
                log_event("notification_not_found", notification_id=notification_id)
                return

            log_event(
                "notification_processing_started", notification_id=notification_id
            )

            imitate_send(notification)

            update_notification_status(
                UUID(notification_id),
                NotificationStatus.SENT,
            )

            log_event("notification_sent", notification_id=notification_id)

        except Exception as exc:
            update_notification_status(
                UUID(notification_id),
                NotificationStatus.FAILED,
                error=str(exc),
            )

            log_event(
                "notification_failed",
                notification_id=notification_id,
                error=str(exc),
            )
