from django.urls import path

from apps.events import views

urlpatterns = [
    path("", views.index, name="index"),
]
