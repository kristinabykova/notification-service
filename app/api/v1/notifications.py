from flask import Blueprint

router = Blueprint("notifications", __name__)


@router.route("/notifications", methods=["POST"])
def create_notification():
    pass


@router.route("/notifications", methods=["GET"])
def get_notification():
    pass


@router.route("/notifications/<uuid:not_id>", methods=["GET"])
def get_notification_by_id(not_id):
    pass
