# Third Party Library
import enum
from logging import Logger

from rest_framework import serializers

from constants import MessageLevel
from finder.telegram_logic.client import TelegramClient


class IntegerLengthValidator:
    def __init__(
            self,
            min_length: int = None,
            max_length: int = None,
            *,
            length: int = None,
    ):
        self.min_length = length or min_length
        self.max_length = length or max_length

    def __call__(self, value):
        length = len(str(value))
        min_length_cond = self.min_length and length < self.min_length
        max_length_cond = self.max_length and length > self.max_length
        if min_length_cond or max_length_cond:
            error = f"Wrong integer parameter length for value {value}"
            raise serializers.ValidationError(error)


LOGGING_MESSAGE_TEMPLATE = "[{level}]{message}"


def operate_message(
        logger: Logger,
        client: TelegramClient,
        message: str,
        level: MessageLevel,
):
    getattr(logger, level.value.lower())(message)
    client.send_message(
        message=message,
        level=level.value,
        template=LOGGING_MESSAGE_TEMPLATE
    )
