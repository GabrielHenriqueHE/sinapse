# urls.py
from django.urls import path

from apps.certificates import views

urlpatterns = [
    path(
        "templates/", views.certificate_template_list, name="certificate_template_list"
    ),
    path(
        "templates/create/",
        views.certificate_template_create,
        name="certificate_template_create",
    ),
    path(
        "templates/<int:pk>/edit/",
        views.certificate_template_update,
        name="certificate_template_update",
    ),
    path(
        "templates/<int:pk>/delete/",
        views.certificate_template_delete,
        name="certificate_template_delete",
    ),
    path(
        "templates/<int:pk>/preview/",
        views.certificate_template_preview,
        name="certificate_template_preview",
    ),
    path(
        "templates/<int:pk>/duplicate/",
        views.certificate_template_duplicate,
        name="certificate_template_duplicate",
    ),
    path(
        "templates/quick-preview/",
        views.certificate_template_quick_preview,
        name="certificate_template_quick_preview",
    ),
    path(
        "templates/<int:pk>/use/<int:event_id>/",
        views.certificate_template_use,
        name="certificate_template_use",
    ),
]
