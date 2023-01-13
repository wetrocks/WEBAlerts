from dataclasses import dataclass
import datetime


@dataclass(frozen=True)
class Alert:
    id: str
    notificationType: str
    created: datetime.datetime
    title: str
    content: str


class AlertRepository:
    def get(self, id: str) -> Alert:
        return None

    def save(self, alert: Alert) -> dict:
        pass
