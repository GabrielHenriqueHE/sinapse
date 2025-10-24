from functools import wraps
from typing import Iterable

from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.views import View

from apps.authentication.models import UserModel


def student_only(view: View):
    @wraps(view)
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("landing_page")

        if (
            not hasattr(request.user, "role")
            or request.user.role != UserModel.Role.STUDENT
        ):
            return HttpResponseForbidden("Acesso negado.")

        return view(request, *args, **kwargs)

    return _wrapped_view


def teacher_only(view: View):
    @wraps(view)
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("landing_page")

        if (
            not hasattr(request.user, "role")
            or request.user.role != UserModel.Role.TEACHER
        ):
            return HttpResponseForbidden("Acesso negado.")

        return view(request, *args, **kwargs)

    return _wrapped_view


def superuser_only(view: View):
    @wraps(view)
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("landing_page")

        if not request.user.is_staff:
            return HttpResponseForbidden("Acesso negado.")

        return view(request, *args, **kwargs)

    return _wrapped_view
