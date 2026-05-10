import re
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
    EmailStr,
)
from db.models import NotificationStatus, NotificationType

PHONE_RE = re.compile(r"^\+?[1-9]\d{7,14}$")
TELEGRAM_RE = re.compile(r"^(@?[A-Za-z0-9_]{5,32}|\d{5,20})$")


class CreateNotification(BaseModel):
    type: NotificationType
    recipient: str = Field(min_length=1, max_length=255)
    subject: Optional[str] = Field(default=None, max_length=255)
    message: str = Field(min_length=1)
    channel_data: Optional[dict[str, Any]]

    @model_validator(mode="after")
    def validate(self):
        if self.type == NotificationType.EMAIL:
            EmailStr._validate(self.recipient)
        elif self.type == NotificationType.SMS:
            if not PHONE_RE.fullmatch(self.recipient):
                raise ValueError("Invalid phone number")
        elif self.type == NotificationType.TELEGRAM:
            if not TELEGRAM_RE.fullmatch(self.recipient):
                raise ValueError("Invalid telegram username or chat id")

        return self


class CreateNotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: NotificationStatus = NotificationStatus.QUEUED


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: NotificationStatus
    error: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("error", "error_text")
    )


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]


class NotificationFilter(BaseModel):
    status: Optional[NotificationStatus] = None
    limit: Optional[int] = Field(default=None, ge=1, le=100)
    offset: Optional[int] = Field(default=None, ge=0)
