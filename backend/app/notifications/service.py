from app.core.config import Settings, get_settings
from app.notifications.base import NotificationMessage, NotificationProvider, NotificationResult
from app.notifications.null import NullNotificationProvider
from app.notifications.telegram import TelegramNotificationProvider


class NotificationService:
    def __init__(
        self,
        provider: NotificationProvider | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.provider = provider or self._build_provider()

    def send(self, message: NotificationMessage) -> NotificationResult:
        return self.provider.send(message)

    def _build_provider(self) -> NotificationProvider:
        provider_name = self.settings.notification_provider.lower()
        if provider_name == "telegram" and self.settings.telegram_bot_token:
            return TelegramNotificationProvider(self.settings.telegram_bot_token)
        return NullNotificationProvider()
