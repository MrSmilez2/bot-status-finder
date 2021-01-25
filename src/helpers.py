# Standard Library
import pickle
from collections import Callable
from functools import wraps
from logging import Logger

# Third Party Library
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
            error = f"{value} - неправильный номер заказа. Ваш заказ должен состоять из 7 цифр"
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


def cached_method(key_function: Callable, timeout: int):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not settings.CACHE_ENABLED:
                return func(*args, **kwargs)

            cache_key = key_function(*args, **kwargs)
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                return pickle.loads(cached_data)

            data = func(*args, **kwargs)
            if data is not None:
                cache.set(cache_key, pickle.dumps(data), timeout)

            return data
        return wrapper
    return decorator
