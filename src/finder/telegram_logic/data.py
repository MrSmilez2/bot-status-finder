# Standard Library
from dataclasses import (
    InitVar,
    dataclass,
    field,
)


@dataclass
class Message:
    message: InitVar[dict]

    chat_id: int = field(init=False)
    order_id: int = field(init=False)

    def __post_init__(self, message: dict):
        raw_message = message.get("message", {})
        self.chat_id = raw_message.get("chat", {}).get("id")
        self.order_id = raw_message.get("text")

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "order_id": self.order_id,
        }
