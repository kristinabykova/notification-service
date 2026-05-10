import pytest
from pydantic import ValidationError

from app.schemas.notifications import CreateNotification, NotificationFilter
from app.db.models import NotificationStatus, NotificationType


def test_valid_email_notification():
    data = CreateNotification(
        type=NotificationType.EMAIL,
        recipient="user@example.com",
        subject="Test",
        message="Hello",
    )

    assert data.type == NotificationType.EMAIL
    assert data.recipient == "user@example.com"
    assert data.message == "Hello"


def test_invalid_email_notification():
    with pytest.raises(ValidationError):
        CreateNotification(
            type=NotificationType.EMAIL,
            recipient="wrong-email",
            subject="Test",
            message="Hello",
        )


def test_invalid_sms_phone():
    with pytest.raises(ValidationError):
        CreateNotification(
            type=NotificationType.SMS,
            recipient="not-phone",
            message="Hello",
        )


def test_valid_telegram_notification():
    data = CreateNotification(
        type=NotificationType.TELEGRAM,
        recipient="@test_user",
        message="Hello",
    )

    assert data.type == NotificationType.TELEGRAM
    assert data.recipient == "@test_user"


def test_notification_filter_validation():
    filters = NotificationFilter(
        status=NotificationStatus.SENT,
        limit=10,
        offset=0,
    )

    assert filters.status == NotificationStatus.SENT
    assert filters.limit == 10
    assert filters.offset == 0
