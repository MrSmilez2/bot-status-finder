# Standard Library
import logging
from time import sleep

# Third Party Library
from django.conf import settings
from django.core.management import BaseCommand

# Application Library
from finder.sheets_logic.event_manager import EventManager

logger = logging.getLogger(f"{settings.PROJECT}.worker")


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            logger.info("Start iteration")
            event_manager = EventManager()
            is_processed = event_manager.process()
            logger.info(f"Finished to proceed event: {is_processed}")
            if not is_processed:
                sleep(settings.EVENT_WORKER_TIMEOUT)
