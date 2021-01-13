# Standard Library
from contextlib import suppress
from dataclasses import asdict
from typing import Any

# Third Party Library
from rest_framework import (
    serializers,
    status,
)
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

# Application Library
from finder.serializers import EventSerializer
from finder.telegram_logic.callbacks import (
    event_error_callback,
    event_success_callback,
)
from finder.telegram_logic.data import Message


class CreateCallbackMixin:
    success_callback: Any = None

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.success_callback(serializer.data)


class TelegramPostMixin:
    error_callback: Any = None

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except serializers.ValidationError as exc:
            with suppress(KeyError, AttributeError, TypeError):
                chat_id = request.data["message"]["chat"]["id"]
                self.error_callback(chat_id, exc)
            return Response(status=status.HTTP_200_OK)


class EventCreateView(TelegramPostMixin, CreateCallbackMixin, CreateAPIView):
    serializer_class = EventSerializer
    success_callback = staticmethod(event_success_callback)
    error_callback = staticmethod(event_error_callback)

    def create(self, request, *args, **kwargs):
        message = Message(request.data)
        serializer = self.get_serializer(data=asdict(message))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
