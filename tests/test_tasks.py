from uuid import uuid4
from unittest.mock import MagicMock, patch

import pytest

from app.db.models import NotificationStatus
from app.tasks import imitate_send, process_notification


@patch("app.tasks.time.sleep")
@patch("app.tasks.log_event")
def test_imitate_send_success(mock_log_event, mock_sleep):
    notification = MagicMock()
    notification.id = uuid4()
    notification.type = "email"
    notification.recipient = "user@example.com"
    notification.message = "Hello"

    imitate_send(notification)

    mock_sleep.assert_called_once_with(1)
    mock_log_event.assert_called_once()


@patch("app.tasks.time.sleep")
@patch("app.tasks.log_event")
def test_imitate_send_failed(mock_log_event, mock_sleep):
    notification = MagicMock()
    notification.id = uuid4()
    notification.type = "email"
    notification.recipient = "user@example.com"
    notification.message = "fail"

    with pytest.raises(RuntimeError, match="Mock notification sending error"):
        imitate_send(notification)

    mock_sleep.assert_called_once_with(1)


@patch("app.tasks.flask_app")
@patch("app.tasks.log_event")
@patch("app.tasks.imitate_send")
@patch("app.tasks.update_notification_status")
@patch("app.tasks.get_notification_by_id")
def test_process_notification_success(
    mock_get_by_id,
    mock_update_status,
    mock_imitate_send,
    mock_log_event,
    mock_flask_app,
):
    notification_id = uuid4()

    notification = MagicMock()
    notification.id = notification_id
    mock_get_by_id.return_value = notification

    mock_flask_app.app_context.return_value.__enter__.return_value = None
    mock_flask_app.app_context.return_value.__exit__.return_value = None

    process_notification.run(str(notification_id))

    mock_get_by_id.assert_called_once_with(notification_id)
    mock_imitate_send.assert_called_once_with(notification)

    mock_update_status.assert_called_once_with(
        notification_id,
        NotificationStatus.SENT,
    )

    mock_log_event.assert_any_call(
        "notification_processing_started",
        notification_id=str(notification_id),
    )
    mock_log_event.assert_any_call(
        "notification_sent",
        notification_id=str(notification_id),
    )


@patch("app.tasks.flask_app")
@patch("app.tasks.log_event")
@patch("app.tasks.imitate_send")
@patch("app.tasks.update_notification_status")
@patch("app.tasks.get_notification_by_id")
def test_process_notification_failed(
    mock_get_by_id,
    mock_update_status,
    mock_imitate_send,
    mock_log_event,
    mock_flask_app,
):
    notification_id = uuid4()

    notification = MagicMock()
    notification.id = notification_id
    mock_get_by_id.return_value = notification

    mock_imitate_send.side_effect = RuntimeError("Mock notification sending error")

    mock_flask_app.app_context.return_value.__enter__.return_value = None
    mock_flask_app.app_context.return_value.__exit__.return_value = None

    process_notification.run(str(notification_id))

    mock_update_status.assert_called_once_with(
        notification_id,
        NotificationStatus.FAILED,
        error="Mock notification sending error",
    )

    mock_log_event.assert_any_call(
        "notification_failed",
        notification_id=str(notification_id),
        error="Mock notification sending error",
    )
