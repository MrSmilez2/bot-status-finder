# Third Party Library
from django.db import transaction

# Application Library
from finder.models import Event


class EventManager:
    def __init__(self):
        self.event = None

    def process_event(self, event: Event):
        event.status = Event.EventStatus.IN_PROGRESS
        event.save()

    def process(self) -> bool:
        is_processed = False
        with transaction.atomic():
            event = Event.objects.select_for_update().filter(
                status=Event.EventStatus.IN_PROGRESS
            ).first()
            if event:
                try:
                    self.process_event(event)
                except Exception as exc:
                    event.set_error(exc)
                else:
                    event.set_success()
                    is_processed = True

        return is_processed
