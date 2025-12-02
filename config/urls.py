from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def custom_403_view(request, exception):
    return render(request, "403.html", status=403)


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


urlpatterns = [
    path("", include("apps.authentication.urls")),
    path("admin/", admin.site.urls),
    path("events/", include("apps.events.urls")),
]
