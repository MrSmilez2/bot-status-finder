# Third Party Library
from rest_framework import serializers

# Application Library
from finder.models import Event
from helpers import IntegerLengthValidator


class EventSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField()
    order_id = serializers.IntegerField(
        validators=[
            IntegerLengthValidator(length=7),
        ]
    )

    class Meta:
        model = Event
        fields = ("chat_id", "order_id")

    def is_valid(self, raise_exception=False):
        self._prepare_data()
        return super().is_valid(raise_exception)

    def _prepare_data(self):
        raw_message = self.initial_data.get("message", {})
        self.initial_data = {
            "chat_id": raw_message.get("chat", {}).get("id"),
            "order_id": raw_message.get("text")
        }
