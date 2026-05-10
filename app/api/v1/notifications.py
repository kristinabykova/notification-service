from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.crud.notifications import (
    create_notif,
    get_notification_by_id,
    get_notifications,
)
from app.utils.logger import log_event
from app.schemas.notifications import (
    CreateNotification,
    CreateNotificationResponse,
    NotificationFilter,
    NotificationListResponse,
    NotificationResponse,
)

router = Blueprint("notifications", __name__)


@router.route("/notifications", methods=["POST"])
def create_notification():
    log_event("notification_request_received")

    try:
        data = CreateNotification.model_validate(request.get_json() or {})
    except ValidationError as error:
        return jsonify({"detail": error.errors(include_context=False)}), 422

    notification = create_notif(data)

    from app.tasks import process_notification

    process_notification.delay(str(notification.id))

    log_event(
        "notification_queued",
        notification_id=str(notification.id),
        type=notification.type,
        recipient=notification.recipient,
    )

    response = CreateNotificationResponse.model_validate(notification)

    return jsonify(response.model_dump(mode="json")), 201


@router.route("/notifications", methods=["GET"])
def get_notifications_list():
    try:
        filters = NotificationFilter.model_validate(request.args.to_dict())
    except ValidationError as error:
        return jsonify({"detail": error.errors(include_context=False)}), 422

    notifications = get_notifications(filters)

    response = NotificationListResponse(
        items=[
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ]
    )

    return jsonify(response.model_dump(mode="json")), 200


@router.route("/notifications/<uuid:notification_id>", methods=["GET"])
def get_notification(notification_id):
    notification = get_notification_by_id(notification_id)

    if notification is None:
        return jsonify({"detail": "Notification not found"}), 404

    response = NotificationResponse.model_validate(notification)

    return jsonify(response.model_dump(mode="json")), 200
