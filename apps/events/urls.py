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
    path("<uuid:id>/attendance", views.event_attendance, name="event_attendance"),
    path("<uuid:id>/finish", views.finish_event, name="finish_event"),
    path("<uuid:id>/close", views.close_event, name="close_event"),
    path("certificates", views.certificates, name="certificates"),
    path(
        "<uuid:id>/certificate", views.generate_certificate, name="generate_certificate"
    ),
]
