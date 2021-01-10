# Third Party Library
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


class Event(models.Model):
    ERROR_MAX_LENGTH = 255

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
    error = models.CharField(
        _("Error"), max_length=ERROR_MAX_LENGTH, null=True, blank=True
    )
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )
    finished_at = models.DateTimeField(_("Finished at"), null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def set_error(self, exc):
        self.status = self.EventStatus.FAILED
        self.error = str(exc)[:self.ERROR_MAX_LENGTH]
        self.save()

    def set_success(self):
        self.status = self.EventStatus.FINISHED
        self.finished_at = now()
        self.save()
