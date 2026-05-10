from uuid import uuid4
from unittest.mock import MagicMock, patch

from app.crud.notifications import (
    create_notif,
    update_notification_status,
)
from app.db.models import NotificationStatus, NotificationType
from app.schemas.notifications import CreateNotification


@patch("app.crud.notifications.db.session")
def test_create_notification(mock_session):
    data = CreateNotification(
        type=NotificationType.EMAIL,
        recipient="user@example.com",
        subject="Test subject",
        message="Hello",
    )

    notification = create_notif(data)

    mock_session.add.assert_called_once_with(notification)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(notification)

    assert notification.type == NotificationType.EMAIL.value
    assert notification.recipient == "user@example.com"
    assert notification.subject == "Test subject"
    assert notification.message == "Hello"


@patch("app.crud.notifications.get_notification_by_id")
@patch("app.crud.notifications.db.session")
def test_update_notification_status_to_sent(mock_session, mock_get_by_id):
    notification = MagicMock()
    mock_get_by_id.return_value = notification

    notification_id = uuid4()

    result = update_notification_status(
        notification_id,
        NotificationStatus.SENT,
    )

    mock_get_by_id.assert_called_once_with(notification_id)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(notification)

    assert result == notification
    assert notification.status == NotificationStatus.SENT.value
    assert notification.error_text is None


@patch("app.crud.notifications.get_notification_by_id")
@patch("app.crud.notifications.db.session")
def test_update_notification_status_to_failed(mock_session, mock_get_by_id):
    notification = MagicMock()
    mock_get_by_id.return_value = notification

    notification_id = uuid4()

    result = update_notification_status(
        notification_id,
        NotificationStatus.FAILED,
        error="Mock error",
    )

    mock_get_by_id.assert_called_once_with(notification_id)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(notification)

    assert result == notification
    assert notification.status == NotificationStatus.FAILED.value
    assert notification.error_text == "Mock error"


@patch("app.crud.notifications.get_notification_by_id")
@patch("app.crud.notifications.db.session")
def test_update_notification_status_when_notification_not_found(
    mock_session,
    mock_get_by_id,
):
    mock_get_by_id.return_value = None

    result = update_notification_status(
        uuid4(),
        NotificationStatus.SENT,
    )

    assert result is None
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()
