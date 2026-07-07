from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationMessage:
    recipient: str
    text: str


@dataclass(frozen=True)
class NotificationResult:
    success: bool
    error_message: str | None = None


class NotificationProvider(ABC):
    @abstractmethod
    def send(self, message: NotificationMessage) -> NotificationResult:
        raise NotImplementedError
