from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.decorators import student_only, teacher_only
from apps.authentication.models import UserModel
from apps.events.forms import EventForm
from apps.events.models import EventModel


def events(request: HttpRequest):
    user = request.user if request.user.is_authenticated else None

    new = EventModel.objects.filter(start_date__gte=timezone.now()).order_by(
        "-created_at"
    )[:10]

    popular = (
        EventModel.objects.filter(start_date__gte=timezone.now())
        .annotate(participants_count=models.Count("participants"))
        .order_by("-participants_count")[:10]
    )

    created = EventModel.objects.none()
    if user and getattr(user, "role", None) == UserModel.Role.TEACHER:
        created = EventModel.objects.filter(user=user).order_by("-created_at")

    enrolled = EventModel.objects.none()
    if user and getattr(user, "role", None) == UserModel.Role.STUDENT:
        enrolled = EventModel.objects.filter(participants=user).order_by("start_date")

    context = {
        "new": new,
        "popular": popular,
        "created": created,
        "enrolled": enrolled,
        "user": user,
    }

    template = loader.get_template("events/index.html")
    return HttpResponse(template.render(context=context, request=request))


@login_required(login_url="landing_page")
@teacher_only
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)

        if form.is_valid():
            try:
                # Criar o objeto evento sem salvar ainda
                event = form.save(commit=False)

                # Definir os campos que não estão no formulário
                event.user = request.user
                event.status = EventModel.Status.OPEN

                # Salvar o evento
                event.save()

                messages.success(request, "Evento criado com sucesso!")
                return redirect("events_index")

            except Exception as e:
                print(e)
                messages.error(request, f"Erro ao criar evento: {str(e)}")
        else:
            # Debug: mostrar erros do formulário no console
            print("Form errors:", form.errors)
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = EventForm()

    context = {"form": form}
    template = loader.get_template("events/create_event.html")
    return HttpResponse(template.render(context, request))


def event_details(request, id):
    template = loader.get_template("events/event_details.html")
    return HttpResponse(template.render(None, request))


def event_attendance_list(request, id):
    template = loader.get_template("events/event_attendance_list.html")
    return HttpResponse(template.render(None, request))
