from app.notifications.base import NotificationMessage, NotificationProvider, NotificationResult


class NullNotificationProvider(NotificationProvider):
    def send(self, message: NotificationMessage) -> NotificationResult:
        return NotificationResult(success=True)
