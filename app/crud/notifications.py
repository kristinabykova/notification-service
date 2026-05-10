from typing import Optional
from uuid import UUID

from sqlalchemy import select

from app.db.models import Notification, NotificationStatus
from app.schemas.notifications import CreateNotification, NotificationFilter
from app.db.base import db


def create_notif(data: CreateNotification) -> Notification:
    notification = Notification(
        type=data.type.value,
        recipient=data.recipient,
        subject=data.subject,
        message=data.message,
    )

    db.session.add(notification)
    db.session.commit()
    db.session.refresh(notification)
    return notification


def get_notification_by_id(not_id: UUID) -> Optional[Notification]:
    query = select(Notification).where(Notification.id == not_id)
    result = db.session.execute(query)
    return result.scalar_one_or_none()


def get_notifications(filters: NotificationFilter) -> list[Notification]:

    query = select(Notification).order_by(Notification.created_at.desc())

    if filters.status is not None:
        query = query.where(Notification.status == filters.status.value)

    if filters.limit is not None:
        query = query.limit(filters.limit)

    if filters.offset is not None:
        query = query.offset(filters.offset)

    result = db.session.execute(query)
    return result.scalars().all()


def update_notification_status(
    not_id: UUID, status: NotificationStatus, error: str | None = None
) -> Optional[Notification]:
    notification = get_notification_by_id(not_id)
    if notification is None:
        return None
    notification.status = status.value
    notification.error_text = error

    db.session.commit()
    db.session.refresh(notification)

    return notification
