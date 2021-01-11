# Standard Library
import enum


class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@enum.unique
class MessageLevel(AutoName):
    DEBUG = enum.auto()
    INFO = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()


@enum.unique
class EventManagerStatus(AutoName):
    IN_PROGRESS = enum.auto()
    SKIP = enum.auto()
    SUCCESS = enum.auto()
    ERROR = enum.auto()
