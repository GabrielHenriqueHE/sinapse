# apps/events/views.py
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
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.lib import colors

from apps.authentication.decorators import student_only, teacher_only
from apps.authentication.models import UserModel
from apps.events.forms import EventForm
from apps.events.models import EventModel, EventParticipantModel


# =====================================================================
# LISTAGEM DE EVENTOS
# =====================================================================

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


# =====================================================================
# CRUD DE EVENTOS
# =====================================================================

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
                messages.error(request, f"Erro ao criar evento: {str(e)}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = EventForm()

    context = {"form": form}
    template = loader.get_template("events/create_event.html")
    return HttpResponse(template.render(context, request))


def event_details(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound()

    context = {"event": event}

    template = loader.get_template("events/event_details.html")
    return HttpResponse(template.render(context=context, request=request))


@login_required(login_url="landing_page")
@student_only
def enroll_event(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound()

    if event.status != EventModel.Status.OPEN:
        messages.error(request, _("Este evento não está aceitando inscrições."))
        return redirect("event_details", id=id)

    if event.is_full:
        messages.error(request, _("Este evento está lotado."))
        return redirect("event_details", id=id)

    if request.user in event.participants.all():
        messages.info(request, _("Você já está inscrito neste evento."))

    event.participants.add(request.user)
    messages.success(request, _("Inscrição realizada com sucesso!"))

    return redirect("event_details", id=id)


@login_required(login_url="landing_page")
@student_only
def cancel_enrollment(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound()

    if request.user not in event.participants.all():
        messages.error(request, _("Você não estava inscrito neste evento."))

    event.participants.remove(request.user)
    messages.success(request, _("Inscrição cancelada com sucesso."))

    return redirect("event_details", id=id)


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
                            context = {
                                "form": form,
                                "event": event,
                                "now": timezone.now(),
                            }
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
                    context = {"form": form, "event": event, "now": timezone.now()}
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

    context = {"form": form, "event": event, "now": timezone.now()}
    template = loader.get_template("events/edit_event.html")
    return HttpResponse(template.render(context, request))


@login_required(login_url="landing_page")
@teacher_only
def close_event(request, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound()

    if not event.user == request.user:
        return HttpResponseForbidden()

    if event.start_date <= timezone.now():
        messages.error(
            request, "Não é possível fechar inscrições de um evento que já começou."
        )
        return redirect("event_details", id=id)

    if event.status == EventModel.Status.CLOSED:
        messages.warning(request, "As inscrições deste evento já estão fechadas.")
        return redirect("event_details", id=id)

    if event.status in [EventModel.Status.CANCELED, EventModel.Status.FINISHED]:
        messages.error(
            request,
            "Não é possível fechar inscrições de um evento cancelado ou finalizado.",
        )
        return redirect("event_details", id=id)

    try:
        event.status = EventModel.Status.CLOSED
        event.save()

        messages.success(
            request,
            "Inscrições fechadas com sucesso! Os participantes atuais mantêm suas vagas.",
        )

    except Exception as e:
        messages.error(request, f"Erro ao fechar inscrições: {str(e)}")

    return redirect("event_details", id=id)


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
    return HttpResponse(template.render(context, request=request))


# =====================================================================
# PRESENÇA E FINALIZAÇÃO
# =====================================================================

@login_required(login_url="landing_page")
@teacher_only
def event_attendance(request: HttpRequest, id):
    event = EventModel.objects.filter(id=id).first()

    if not event:
        return HttpResponseNotFound("Não foi possível localizar o evento")

    if request.user != event.user:
        return redirect("event_details", id=id)

    if event.end_date <= timezone.now() and event.status != EventModel.Status.FINISHED:
        auto_finish_event(event)
        event.refresh_from_db()

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

                if (
                    event.end_date <= timezone.now()
                    and event.status != EventModel.Status.FINISHED
                ):
                    auto_finish_event(event)
                    event.refresh_from_db()

            except Exception:
                messages.error(request, "Erro ao atualizar.")

        return redirect("event_attendance", id=id)

    participants = event.participants_records.all()

    present_count = participants.filter(status="PRESENT").count()
    total_count = participants.count()

    context = {
        "event": event,
        "participants": participants,
        "present_count": present_count,
        "total_count": total_count,
    }

    template = loader.get_template("events/event_attendance_list.html")
    return HttpResponse(template.render(context, request=request))


@login_required(login_url="landing_page")
@teacher_only
def finish_event(request: HttpRequest, id: int):
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
    return HttpResponse(template.render(context, request=request))


# =====================================================================
# NOVA FUNÇÃO — CERTIFICADO VIA PLATYPUS/REPORTLAB (PDF-native)
# =====================================================================

@login_required(login_url="landing_page")
@student_only
def generate_certificate(request, id):
    """
    Gera um PDF de certificado estilizado usando ReportLab Platypus.
    Design inspirado no template HTML original, mas desenhado com flowables
    — roda em Windows/Linux sem dependências externas além do ReportLab.
    """
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

    # tentar finalizar automaticamente se aplicável
    if event.status != EventModel.Status.FINISHED:
        was_finished = auto_finish_event(event)
        if not was_finished:
            messages.error(
                request,
                "O certificado estará disponível após a finalização do evento e confirmação de presença.",
            )
            return redirect("event_details", id=id)
        else:
            event.refresh_from_db()

    try:
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=f"Certificado - {event.name}",
        )

        # Styles
        base_styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "certificate_title",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4F46E5"),
            spaceAfter=12,
        )

        normal_center = ParagraphStyle(
            "normal_center",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#374151"),
            leading=22,
        )

        participant_style = ParagraphStyle(
            "participant",
            parent=base_styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=34,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4F46E5"),
            leading=36,
            spaceAfter=6,
        )

        event_style = ParagraphStyle(
            "event",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#8B5CF6"),
            leading=28,
            spaceAfter=6,
        )

        details_style = ParagraphStyle(
            "details",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4B5563"),
            leading=20,
            spaceAfter=6,
        )

        # Story setup
        story = []

        # Header / Title
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph("CERTIFICADO DE PARTICIPAÇÃO", title_style))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("Certificamos que", normal_center))
        story.append(Spacer(1, 0.2 * cm))

        participant_name = f"{request.user.first_name} {request.user.last_name}"
        story.append(Paragraph(participant_name, participant_style))
        story.append(Spacer(1, 0.2 * cm))

        story.append(Paragraph("participou com sucesso do evento", normal_center))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph(event.name, event_style))
        story.append(Spacer(1, 0.3 * cm))

        # Calcular carga horária (diferença entre start_date e end_date)
        if event.start_date and event.end_date:
            # Calcular diferença em horas
            time_difference = event.end_date - event.start_date
            total_hours = time_difference.total_seconds() / 3600
            # Arredondar para 1 casa decimal
            duration_hours = round(total_hours, 1)
            
            # Formatar datas para exibição
            start_date_str = event.start_date.strftime("%d/%m/%Y %H:%M")
            end_date_str = event.end_date.strftime("%d/%m/%Y %H:%M")
            
            # Verificar se é no mesmo dia
            if event.start_date.date() == event.end_date.date():
                date_range_str = f"<b>{event.start_date.strftime('%d/%m/%Y')}</b><br/>"
                time_range_str = f"Das <b>{event.start_date.strftime('%H:%M')}</b> às <b>{event.end_date.strftime('%H:%M')}</b>"
            else:
                date_range_str = f"De <b>{event.start_date.strftime('%d/%m/%Y %H:%M')}</b><br/>"
                time_range_str = f"Até <b>{event.end_date.strftime('%d/%m/%Y %H:%M')}</b>"
        else:
            duration_hours = 0
            date_range_str = "Data não especificada"
            time_range_str = ""

        # Event details block
        details_html = (
            f"Realizado em <b>{event.city}, {event.state} - {event.country}</b><br/>"
            f"{date_range_str}"
            f"{time_range_str}<br/>"
            f"Carga horária total de <b>{duration_hours} horas</b>"
        )
        story.append(Paragraph(details_html, details_style))
        story.append(Spacer(1, 1.2 * cm))

        # Data de emissão
        emission_date = timezone.now().strftime("%d/%m/%Y")
        emission_text = f"Emitido digitalmente em {emission_date} através da plataforma Sinapse"
        story.append(Paragraph(emission_text, ParagraphStyle(
            "emission",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#6B7280"),
            leading=16,
        )))
        story.append(Spacer(1, 0.6 * cm))

        # ID do certificado
        cert_id = (
            f"SNSP-{timezone.now().strftime('%Y%m%d')}-"
            f"{(request.user.first_name[:1] or '').upper()}{(request.user.last_name[:1] or '').upper()}-"
            f"{(event.name[:3] or '').upper()}"
        )
        cert_para = Paragraph(cert_id, ParagraphStyle(
            "cert_id",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#9CA3AF"),
        ))
        story.append(cert_para)

        def draw_background(canvas_obj, doc_obj):
            w, h = landscape(A4)
            canvas_obj.saveState()

            # Background fill
            canvas_obj.setFillColor(colors.HexColor("#F3F4F6"))
            canvas_obj.rect(0, 0, w, h, stroke=0, fill=1)

            # Outer decorative border
            canvas_obj.setStrokeColor(colors.HexColor("#4F46E5"))
            canvas_obj.setLineWidth(10)
            canvas_obj.rect(20, 20, w - 40, h - 40, stroke=1, fill=0)

            # Inner subtle border
            canvas_obj.setStrokeColor(colors.Color(0.545, 0.361, 0.961, alpha=0.18))
            canvas_obj.setLineWidth(2)
            canvas_obj.rect(36, 36, w - 72, h - 72, stroke=1, fill=0)

            # Central watermark "SINAPSE"
            watermark_color = colors.Color(79/255, 70/255, 229/255, alpha=0.06)
            canvas_obj.setFillColor(watermark_color)
            canvas_obj.setFont("Helvetica-Bold", 120)

            canvas_obj.saveState()
            canvas_obj.translate(w / 2.0, h / 2.0)
            canvas_obj.rotate(-25)
            canvas_obj.drawCentredString(0, 0, "SINAPSE")
            canvas_obj.restoreState()

            # Footer ID
            canvas_obj.setFillColor(colors.HexColor("#D1D5DB"))
            canvas_obj.setFont("Helvetica", 9)
            canvas_obj.drawRightString(w - 30, 25, f"Certificado ID: {cert_id}")

            canvas_obj.restoreState()

        # Build PDF
        doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)

        pdf_value = buffer.getvalue()
        buffer.close()

        filename = f"certificado_{slugify(event.name)}_{slugify(request.user.first_name)}_{slugify(request.user.last_name)}.pdf"
        response = HttpResponse(pdf_value, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        # Logging em stdout para facilitar debug (substitua por logger se desejar)
        print(f"Erro ao gerar certificado: {e}")
        messages.error(request, "Ocorreu um erro ao gerar o certificado.")
        return redirect("event_details", id=id)


# =====================================================================
# LISTAGEM DE CERTIFICADOS
# =====================================================================

@login_required(login_url="landing_page")
@student_only
def certificates(request):
    user_participations = EventParticipantModel.objects.filter(
        user=request.user
    ).select_related("event")

    for participation in user_participations:
        event = participation.event
        if event.end_date <= timezone.now() and event.status not in [
            EventModel.Status.FINISHED,
            EventModel.Status.CANCELED,
        ]:
            auto_finish_event(event)

    available_certificates = EventParticipantModel.objects.filter(
        user=request.user,
        status=EventParticipantModel.ParticipationStatus.PRESENT,
        event__status=EventModel.Status.FINISHED,
    ).select_related("event")

    print(available_certificates)

    context = {"available_certificates": available_certificates}

    template = loader.get_template("events/my_certificates.html")
    return HttpResponse(template.render(context=context, request=request))


# =====================================================================
# AUXILIARES
# =====================================================================

def auto_finish_event(event: EventModel) -> bool:
    """
    Finaliza automaticamente um evento se:
    1. A data de término já passou
    2. O evento não está cancelado
    3. A lista de chamada foi feita (pelo menos um participante com status definido)
    Retorna True se o evento foi finalizado, False caso contrário
    """
    if event.status in [EventModel.Status.FINISHED, EventModel.Status.CANCELED]:
        return False

    if event.end_date > timezone.now():
        return False

    # Verificar se há pelo menos um participante com status definido (lista de chamada feita)
    has_attendance_records = event.participants_records.filter(
        status__in=["PRESENT", "ABSENT"]
    ).exists()

    if not has_attendance_records:
        return False

    try:
        event.status = EventModel.Status.FINISHED
        event.save()
        return True
    except Exception:
        return False


def can_generate_certificates(event: EventModel) -> bool:
    """
    Verifica se o evento está em condições de gerar certificados
    """
    return (
        event.status == EventModel.Status.FINISHED
        and event.end_date <= timezone.now()
        and event.participants_records.filter(status="PRESENT").exists()
    )
