# Standard Library
from typing import Optional

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
    EventErrorCallback,
    EventSuccessCallback,
    event_error_callback,
    event_success_callback,
)


class CreateCallbackMixin:
    success_callback: Optional[EventSuccessCallback] = None

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.success_callback(serializer.data)


class TelegramPostMixin:
    error_callback: Optional[EventErrorCallback] = None

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except serializers.ValidationError as exc:
            self.error_callback(request, exc)
            return Response(status=status.HTTP_200_OK)


class EventCreateView(TelegramPostMixin, CreateCallbackMixin, CreateAPIView):
    serializer_class = EventSerializer
    success_callback = event_success_callback
    error_callback = event_error_callback
