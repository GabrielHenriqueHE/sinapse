from django.urls import path

from apps.events import views

urlpatterns = [
    path("", views.events, name="events_index"),
    path("create", views.create_event, name="create_event"),
    path("<uuid:id>", views.event_details, name="event_details"),
    path("<uuid:id>/enroll", views.enroll_event, name="enroll_event"),
    path(
        "<uuid:id>/cancel_enrollment", views.cancel_enrollment, name="cancel_enrollment"
    ),
    path("<uuid:id>/edit", views.edit_event, name="edit_event"),
    path("<uuid:id>/cancel", views.cancel_event, name="cancel_event"),
]
