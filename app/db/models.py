import enum

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import pk_uuid, created_time, updated_time, db


class NotificationType(str, enum.Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"
    SMS = "sms"


class NotificationStatus(str, enum.Enum):
    QUEUED = "queued"
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(db.Model):
    __tablename__ = "notifications"

    id: Mapped[pk_uuid]

    type: Mapped[str] = mapped_column(String(20))
    recipient: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str | None] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        String(20),
        default=NotificationStatus.QUEUED.value,
        index=True,
    )

    error_text: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[created_time]
    updated_at: Mapped[updated_time]
