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
