# Standard Library
from contextlib import suppress
from typing import (
    Any,
    Callable,
    Dict,
)

# Third Party Library
from rest_framework.request import Request
from rest_framework.response import Response

# Application Library
from finder.telegram_logic.client import TelegramClient
from finder.telegram_logic.constants import ERROR_LENGTH

__all__ = (
    "event_success_callback",
    "event_error_callback",
    "EventSuccessCallback",
    "EventErrorCallback",
)


SUCCESS_MESSAGE_TEMPLATE = "Event searching order {order_id} has been created"

EventSuccessCallback = Callable[[Any, Dict[str, str]], Response]
EventErrorCallback = Callable[[Any, Request, Exception], Response]


def event_success_callback(_, data: Dict[str, str]):
    client = TelegramClient()
    chat_id = data["chat_id"]
    order_id = data["order_id"]
    client.send_message(
        chat_id,
        {"order_id": order_id},
        template=SUCCESS_MESSAGE_TEMPLATE
    )


def event_error_callback(_, request: Request, exc: Exception):
    client = TelegramClient()
    with suppress(KeyError):
        chat_id = request.data["message"]["chat"]["id"]
        client.send_message(
            chat_id,
            {"message": str(exc)[:ERROR_LENGTH]},
        )
