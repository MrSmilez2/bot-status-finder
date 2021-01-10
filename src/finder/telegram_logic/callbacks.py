# Standard Library
from typing import Dict

# Application Library
from finder.telegram_logic.client import TelegramClient
from finder.telegram_logic.constants import ERROR_LENGTH

__all__ = (
    "event_success_callback",
    "event_error_callback",
)


SUCCESS_MESSAGE_TEMPLATE = "Event searching order {order_id} has been created"


def event_success_callback(data: Dict[str, str]):
    client = TelegramClient()
    chat_id = data["chat_id"]
    order_id = data["order_id"]
    client.send_message(
        chat_id,
        {"order_id": order_id},
        template=SUCCESS_MESSAGE_TEMPLATE
    )


def event_error_callback(chat_id, exc: Exception):
    client = TelegramClient()
    client.send_message(
        chat_id,
        {"message": str(exc)[:ERROR_LENGTH]},
    )
