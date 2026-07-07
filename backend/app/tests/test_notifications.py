from app.notifications import NotificationMessage, NullNotificationProvider


def test_null_notification_provider_does_not_send_real_messages() -> None:
    provider = NullNotificationProvider()

    result = provider.send(NotificationMessage(recipient="123", text="hello"))

    assert result.success is True
    assert result.error_message is None
