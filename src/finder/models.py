# Third Party Library
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    class EventStatus(models.TextChoices):
        WAITING = "WAITING", _("Waiting")
        IN_PROGRESS = "IN_PROGRESS", _("In progress")
        FINISHED = "FINISHED", _("Finished")
        FAILED = "FAILED", _("Failed")

    chat_id = models.IntegerField(_("Chat id"))
    order_id = models.IntegerField(_("Order id"))
    status = models.CharField(
        _("Status"),
        max_length=255,
        choices=EventStatus.choices,
        default=EventStatus.WAITING,
    )
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )
    finished_at = models.DateTimeField(_("Finished at"), null=True)
