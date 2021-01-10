# Third Party Library
import requests
from django.conf import settings


class TelegramClient:
    BASE_URL = "https://api.telegram.org/bot{token}/"
    BOT_URL = BASE_URL.format(token=settings.TELEGRAM_TOKEN)
    SEND_MESSAGE_URL = f"{BOT_URL}sendMessage"

    def send_message(self, chat_id, data, template=None):
        message = template.format(**data) if template else data["message"]
        url = self.SEND_MESSAGE_URL.format(chat_id=chat_id, message=message)
        requests.get(
            url, params={
                "chat_id": chat_id,
                "text": message,
            }
        )
