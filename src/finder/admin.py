# Third Party Library
from django.contrib import admin

# Application Library
# Register your models here.
from finder.models import Event


class EventAdmin(admin.ModelAdmin):
    pass


admin.site.register(Event, EventAdmin)
