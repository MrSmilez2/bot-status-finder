# Standard Library
import logging
from typing import Optional

# Third Party Library
from django.conf import settings
from django.db import transaction

# Application Library
from constants import (
    EventManagerStatus,
    MessageLevel,
)
from finder.gspread_logic.client import (
    GSpreadClient,
    get_gspread_client,
)
from finder.models import Event
from finder.telegram_logic.client import TelegramClient
from helpers import operate_message

logger = logging.getLogger(f"{settings.PROJECT}.event")


class EventManager:
    def __init__(self):
        self.gspread_client: GSpreadClient = get_gspread_client()
        self.error: Optional[str] = None
        self.status: EventManagerStatus = EventManagerStatus.IN_PROGRESS

        self.event: Optional[Event] = None
        self.chat_id: Optional[int] = None
        self.client: Optional[TelegramClient] = None

    def post_init(self):
        self.event = Event.objects.select_for_update().filter(
            status=Event.EventStatus.WAITING
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
        self.event.set_in_progress()

    def process(self):
        with transaction.atomic():
            self.post_init()
            if self.event:
                try:
                    self.process_event()
                except Exception as exc:
                    self._operate_error(exc)
                else:
                    self._operate_success()
            else:
                self.status = EventManagerStatus.SKIP
