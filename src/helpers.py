# Standard Library
import pickle
from collections import Callable
from functools import wraps
from logging import Logger

# Third Party Library
from typing import Union

from django.conf import settings
from django.core.cache import cache
from rest_framework import serializers

# Application Library
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


def cached_method(cache_key: Union[Callable, str], timeout: int):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not settings.CACHE_ENABLED:
                return func(*args, **kwargs)
            key = cache_key(*args, **kwargs) \
                if callable(cache_key) else cache_key
            cached_data = cache.get(key)

            if cached_data is not None:
                return pickle.loads(cached_data)

            data = func(*args, **kwargs)
            if data is not None:
                cache.set(key, pickle.dumps(data), timeout)

            return data
        return wrapper
    return decorator
