import httpx

from app.notifications.base import NotificationMessage, NotificationProvider, NotificationResult


class TelegramNotificationProvider(NotificationProvider):
    def __init__(self, bot_token: str, *, timeout_seconds: float = 10.0) -> None:
        self.bot_token = bot_token
        self.timeout_seconds = timeout_seconds

    def send(self, message: NotificationMessage) -> NotificationResult:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            response = httpx.post(
                url,
                json={
                    "chat_id": message.recipient,
                    "text": message.text,
                    "disable_web_page_preview": False,
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except Exception as exc:
            return NotificationResult(success=False, error_message=str(exc))
        return NotificationResult(success=True)
