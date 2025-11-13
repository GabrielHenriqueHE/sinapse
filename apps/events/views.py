import os
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from apps.authentication.decorators import student_only, teacher_only
from apps.authentication.models import UserModel
from apps.events.forms import EventForm
from apps.events.models import EventModel, EventParticipantModel


def events(request: HttpRequest):
    # EventModel.objects.filter(
    #     start_date__lte=timezone.now(), status__in=[EventModel.Status.OPEN]
    # ).update(status=EventModel.Status.CLOSED)

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
            messages.error(request, f"Erro ao cancelar evento: {str(e)}")
            return redirect("event_details", id=id)

    context = {"event": event}
    template = loader.get_template("events/cancel_event.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url="landing_page")
@teacher_only
def event_attendance(request: HttpRequest, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound("Não foi possível localizar o evento")

    if request.user != event.user:
        return redirect("event_details", id=id)

    if event.end_date > timezone.now():
        return redirect("event_details", id=id)

    if request.method == "POST":
        participant_id = request.POST.get("participant_id")
        status = request.POST.get("status")

        if participant_id and status in ["PRESENT", "ABSENT"]:
            try:
                record = event.participants_records.get(id=participant_id)
                record.status = status
                record.save()
                messages.success(
                    request, f"Status de {record.user.get_full_name()} atualizado."
                )
            except Exception as e:
                messages.error(request, "Erro ao atualizar.")

        return redirect("event_attendance", id=id)

    # Busca participantes
    participants = event.participants_records.all()

    # Calcula estatísticas
    present_count = participants.filter(status="PRESENT").count()
    total_count = participants.count()

    context = {
        "event": event,
        "participants": participants,
        "present_count": present_count,
        "total_count": total_count,
    }

    template = loader.get_template("events/event_attendance_list.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url="landing_page")
@teacher_only
def finish_event(request: HttpRequest, id: int):
    """View para finalizar evento após lista de chamada"""
    event = get_object_or_404(EventModel, id=id)

    if request.user != event.user:
        messages.error(request, "Você não tem permissão para finalizar este evento.")
        return redirect("event_details", id=id)

    if event.end_date > timezone.now():
        messages.error(
            request,
            "O evento ainda não terminou. Aguarde a data de término para finalizar.",
        )
        return redirect("event_attendance", id=id)

    if event.status == EventModel.Status.FINISHED:
        messages.info(request, "Este evento já está finalizado.")
        return redirect("event_details", id=id)

    if request.method == "POST":
        try:
            EventModel.objects.filter(id=event.id).update(
                status=EventModel.Status.FINISHED, updated_at=timezone.now()
            )

            messages.success(
                request, "Evento finalizado com sucesso! As edições foram bloqueadas."
            )
            return redirect("event_details", id=id)

        except Exception as e:
            messages.error(request, f"Erro ao finalizar evento: {str(e)}")
            return redirect("event_attendance", id=id)

    context = {"event": event}
    template = loader.get_template("events/finish_event.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url="landing_page")
@student_only
def generate_certificate(request, id):
    event = get_object_or_404(EventModel, id=id)

    participation = EventParticipantModel.objects.filter(
        event=event, user=request.user
    ).first()

    if (
        not participation
        or participation.status != EventParticipantModel.ParticipationStatus.PRESENT
    ):
        messages.error(
            request,
            "Você não esteve presente neste evento ou não tem permissão para gerar o certificado.",
        )
        return redirect("event_details", id=id)

    if event.status != EventModel.Status.FINISHED:
        messages.error(
            request, "O certificado estará disponível após a finalização do evento."
        )
        return redirect("event_details", id=id)

    try:
        buffer = BytesIO()

        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        p.setTitle(f"Certificado - {event.name}")

        p.setFillColor(colors.HexColor("#F3F4F6"))
        p.rect(0, 0, width, height, fill=1)

        p.setStrokeColor(colors.HexColor("#4F46E5"))
        p.setLineWidth(10)
        p.rect(20, 20, width - 40, height - 40, stroke=1, fill=0)

        p.setFillColor(colors.HexColor("#4F46E5"))
        p.setFont("Helvetica-Bold", 28)
        p.drawCentredString(width / 2, height - 100, "CERTIFICADO DE PARTICIPAÇÃO")

        p.setFillColor(colors.black)
        p.setFont("Helvetica", 16)
        p.drawCentredString(width / 2, height - 160, "Certificamos que")

        p.setFillColor(colors.HexColor("#1F2937"))
        p.setFont("Helvetica-Bold", 32)
        participant_name = f"{request.user.first_name} {request.user.last_name}"
        p.drawCentredString(width / 2, height - 220, participant_name)

        p.setFillColor(colors.black)
        p.setFont("Helvetica", 16)
        p.drawCentredString(width / 2, height - 280, "participou com sucesso do evento")

        p.setFillColor(colors.HexColor("#8B5CF6"))
        p.setFont("Helvetica-Bold", 24)
        p.drawCentredString(width / 2, height - 340, event.name)

        p.setFillColor(colors.HexColor("#4B5563"))
        p.setFont("Helvetica", 14)
        p.drawCentredString(
            width / 2,
            height - 400,
            f"Realizado em {event.city}, {event.state} - {event.country}",
        )
        p.drawCentredString(
            width / 2,
            height - 430,
            f"No período de {event.start_date.strftime('%d/%m/%Y')} a {event.end_date.strftime('%d/%m/%Y')}",
        )

        p.setStrokeColor(colors.HexColor("#4F46E5"))
        p.setLineWidth(1)
        p.line(100, 150, 300, 150)
        p.line(width / 2 - 100, 150, width / 2 + 100, 150)
        p.line(width - 300, 150, width - 100, 150)
        p.setFillColor(colors.HexColor("#6B7280"))
        p.setFont("Helvetica", 12)
        p.drawCentredString(200, 130, "Organizador do Evento")
        p.drawCentredString(width / 2, 130, "Plataforma Sinapse")
        p.drawCentredString(width - 200, 130, "Data de Emissão")

        p.setFillColor(colors.HexColor("#1F2937"))
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(200, 100, event.user.get_full_name() or "Organizador")
        p.drawCentredString(width / 2, 100, "Conectando Pessoas")
        p.drawCentredString(width - 200, 100, timezone.now().strftime("%d/%m/%Y"))

        p.setFillColor(colors.HexColor("#6B7280"))
        p.setFont("Helvetica", 10)
        p.drawCentredString(
            width / 2, 50, "Certificado emitido digitalmente pela plataforma Sinapse"
        )

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(content_type="application/pdf")
        filename = f"certificado_{slugify(event.name)}_{slugify(request.user.first_name)}_{slugify(request.user.last_name)}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(pdf)

        return response

    except Exception as e:
        print(f"Erro ao gerar certificado: {str(e)}")
        messages.error(request, "Ocorreu um erro ao gerar o certificado.")
        return redirect("event_details", id=id)


@login_required(login_url="landing_page")
@student_only
def certificates(request):
    participations = EventParticipantModel.objects.filter(
        user=request.user, status=EventParticipantModel.ParticipationStatus.PRESENT
    ).select_related("event")

    available_certificates = [
        participation
        for participation in participations
        if participation.event.status == EventModel.Status.FINISHED
    ]

    context = {"available_certificates": available_certificates}

    template = loader.get_template("events/my_certificates.html")
    return HttpResponse(template.render(context=context, request=request))
