from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.authentication.urls")),
    path("admin/", admin.site.urls),
    path("events/", include("apps.events.urls")),
    path("certificates/", include("apps.certificates.urls")),
]
