from django.urls import path

from apps.events import views

urlpatterns = [
    path("", views.events, name="events_index"),
    path("create", views.create_event, name="create_event"),
    path("<uuid:id>", views.event_details, name="event_details")
]
