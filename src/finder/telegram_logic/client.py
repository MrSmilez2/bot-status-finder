# Third Party Library
import requests
from django.conf import settings


class TelegramClient:
    BASE_URL = "https://api.telegram.org/bot{token}/"
    BOT_URL = BASE_URL.format(token=settings.TELEGRAM_TOKEN)
    SEND_MESSAGE_URL = f"{BOT_URL}sendMessage"

    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def send_message(
            self,
            message: str = None,
            template: str = "{message}",
            **kwargs
    ):
        message_data = {"message": message} if message is not None else {}
        message_data.update(**kwargs)
        requests.get(
            self.SEND_MESSAGE_URL, params={  # type: ignore
                "chat_id": self.chat_id,
                "text": template.format(**message_data),
            }
        )
