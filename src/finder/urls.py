# Third Party Library
from django.urls import path

# Application Library
from finder.views import EventCreateView

urlpatterns = [
    path("", EventCreateView.as_view(), name="create-event"),
]
