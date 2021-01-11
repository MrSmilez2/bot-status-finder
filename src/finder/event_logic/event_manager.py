# Standard Library
import logging
from dataclasses import (
    dataclass,
    field,
)
from typing import Optional

# Third Party Library
from django.conf import settings
from django.db import transaction

# Application Library
from constants import (
    EventManagerStatus,
    MessageLevel,
)
from finder.gspread_logic.client import GSpreadClient
from finder.models import Event
from finder.telegram_logic.client import TelegramClient
from helpers import operate_message

logger = logging.getLogger(f"{settings.PROJECT}.event")


@dataclass
class EventManager:
    gspread_client: GSpreadClient
    error: Optional[str] = field(init=False, default=None)
    status: EventManagerStatus = field(
        default=EventManagerStatus.IN_PROGRESS,
        init=False,
    )

    event: Event = field(init=False)
    chat_id: int = field(init=False)
    client: TelegramClient = field(init=False)

    def __post_init__(self):
        self.event = Event.objects.select_for_update().filter(
            status=Event.EventStatus.IN_PROGRESS
        ).first()
        self.chat_id = self.event and self.event.chat_id
        self.client = self.event and TelegramClient(self.chat_id)

    def _operate_success(self):
        self.event.set_success()
        self.status = EventManagerStatus.SUCCESS
        message = f"Event {self.event.pk} operated successfully"
        operate_message(logger, self.client, message, MessageLevel.INFO)

    def _operate_error(self, exc):
        self.event.set_error(exc)
        self.error = self.event.error
        self.status = EventManagerStatus.ERROR
        message = f"Event {self.event.pk} failed with error: {self.error}"
        operate_message(logger, self.client, message, MessageLevel.ERROR)

    def process_event(self):
        if not self.event:
            self.status = EventManagerStatus.SKIP
            return

        self.event.set_in_progress()

    def process(self):
        with transaction.atomic():
            try:
                self.process_event()
            except Exception as exc:
                self._operate_error(exc)
            else:
                self._operate_success()
