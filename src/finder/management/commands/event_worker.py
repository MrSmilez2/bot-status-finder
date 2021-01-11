# Standard Library
import logging
from time import sleep

# Third Party Library
from django.conf import settings
from django.core.management import BaseCommand

# Application Library
from constants import EventManagerStatus
from finder.event_logic.event_manager import EventManager
from finder.gspread_logic.client import GSpreadClient

logger = logging.getLogger(f"{settings.PROJECT}.worker")


class Command(BaseCommand):
    def handle(self, *args, **options):
        gspread_client = GSpreadClient()

        while True:
            logger.info("Start iteration")
            event_manager = EventManager(gspread_client)
            event_manager.process()
            logger.info(
                f"Finished to proceed event "
                f"{event_manager.event.pk if event_manager.event else ''}: "
                f"{event_manager.status}"
            )
            if event_manager.status == EventManagerStatus.ERROR:
                logger.error(
                    f"Event {event_manager.event.pk} failed with error: "
                    f"{event_manager.error}"
                )
            sleep(settings.EVENT_WORKER_TIMEOUT)
