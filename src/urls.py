# Third Party Library
from django.contrib import admin
from django.urls import (
    include,
    path,
)

# Application Library
from finder import urls as finder_urls

urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += [
    path("", include(finder_urls)),
]
