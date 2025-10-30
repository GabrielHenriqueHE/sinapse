from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
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
                event = form.save(commit=False)

                event.user = request.user
                event.status = EventModel.Status.OPEN

                event.save()

                messages.success(request, "Evento criado com sucesso!")
                return redirect("events_index")

            except Exception as e:
                print(e)
                messages.error(request, f"Erro ao criar evento: {str(e)}")
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = EventForm()

    context = {"form": form}
    template = loader.get_template("events/create_event.html")
    return HttpResponse(template.render(context, request))


def event_details(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return (
            HttpResponseNotFound()
        )  # TODO: adicionar redirect para uma view user-friendly

    context = {"event": event}

    template = loader.get_template("events/event_details.html")
    return HttpResponse(template.render(context=context, request=request))


@login_required(login_url="landing_page")
@student_only
def enroll_event(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return (
            HttpResponseNotFound()
        )  # TODO: adicionar redirect para uma view user-friendly

    if event.status != EventModel.Status.OPEN:
        messages.error(
            request=request, message=_("Este evento não está aceitando inscrições.")
        )
        return redirect(to="event_details", id=id)

    if event.is_full:
        messages.error(request=request, message=_("Este evento está lotado."))
        return redirect(to="event_details", id=id)

    if request.user in event.participants.all():
        messages.info(request=request, message=_("Você já está inscrito neste evento."))

    event.participants.add(request.user)
    messages.success(request=request, message=_("Inscrição realizada com sucesso!"))

    return redirect(to="event_details", id=id)


@login_required(login_url="landing_page")
@student_only
def cancel_enrollment(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return (
            HttpResponseNotFound()
        )  # TODO: adicionar redirect para uma view user-friendly

    if request.user not in event.participants.all():
        messages.error(
            request=request, message=_("Você não estava inscrito neste evento.")
        )

    event.participants.remove(request.user)
    messages.success(request=request, message=_("Inscrição cancelada com sucesso."))

    return redirect(to="event_details", id=id)


@login_required(login_url="landing_page")
@teacher_only
def edit_event(request: HttpRequest, id: int):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound()

    if request.user != event.user:
        messages.error(request, "Você não tem permissão para editar este evento.")
        return redirect("event_details", id=id)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            try:
                updated = form.save(commit=False)

                status = request.POST.get("status")
                if status in dict(EventModel.Status.choices):
                    updated.status = status

                if event.start_date > timezone.now():
                    if updated.start_date and updated.end_date:
                        if updated.start_date >= updated.end_date:
                            messages.error(
                                request,
                                "A data de término deve ser posterior à data de início.",
                            )
                            context = {"form": form, "event": event}
                            template = loader.get_template("events/edit_event.html")
                            return HttpResponse(template.render(context, request))

                if (
                    updated.participants_limit is not None
                    and updated.participants_limit < event.participants.count()
                ):
                    messages.error(
                        request,
                        f"Não é possível definir o limite para {updated.participants_limit} "
                        f"porque o evento já tem {event.participants.count()} participantes.",
                    )
                    context = {"form": form, "event": event}
                    template = loader.get_template("events/edit_event.html")
                    return HttpResponse(template.render(context, request))

                updated.save()
                messages.success(request, "Evento atualizado com sucesso!")
                return redirect("event_details", id=updated.id)

            except Exception as e:
                messages.error(request, f"Erro ao atualizar evento: {str(e)}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = EventForm(instance=event)

    context = {"form": form, "event": event}
    template = loader.get_template("events/edit_event.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url="landing_page")
@teacher_only
def cancel_event(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound()

    if request.user != event.user:
        messages.error(request, "Você não tem permissão para cancelar este evento.")
        return redirect("event_details", id=id)

    if request.method == "POST":
        try:
            if event.status == EventModel.Status.CANCELED:
                messages.info(request, "Este evento já está cancelado.")
                return redirect("event_details", id=id)

            event.status = EventModel.Status.CANCELED
            event.save()

            messages.success(request, "Evento cancelado com sucesso!")
            return redirect("event_details", id=id)

        except Exception as e:
            print(e)
            messages.error(request, f"Erro ao cancelar evento: {str(e)}")
            return redirect("event_details", id=id)

    context = {"event": event}
    template = loader.get_template("events/cancel_event.html")
    return HttpResponse(template.render(context, request))


def event_attendance_list(request, id):
    template = loader.get_template("events/event_attendance_list.html")
    return HttpResponse(template.render(None, request))
