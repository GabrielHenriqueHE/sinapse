from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.template import loader

from apps.authentication.decorators import teacher_only
from apps.certificates.forms import CertificateTemplateForm
from apps.certificates.models import CertificateTemplateModel


@login_required
@teacher_only
def certificate_template_list(request):
    """Lista todos os templates de certificado do usuário"""
    templates = CertificateTemplateModel.objects.filter(user=request.user)

    context = {"templates": templates}

    template = loader.get_template("certificate_template_list.html")

    return HttpResponse(template.render(context=context, request=request))


@login_required
@teacher_only
def certificate_template_create(request):
    """Cria um novo template de certificado"""
    if request.method == "POST":
        form = CertificateTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, "Template criado com sucesso!")
            return redirect("certificate_template_list")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CertificateTemplateForm()

    context = {"form": form}

    template = loader.get_template("create_certificate_template.html")

    return HttpResponse(template.render(context=context, request=request))


@login_required
@teacher_only
def certificate_template_update(request, id):
    """Atualiza um template de certificado existente"""
    certificate_template = CertificateTemplateModel.objects.filter(
        id=id, user=request.user
    )

    if not certificate_template:
        return HttpResponseNotFound(
            "Não foi possível localizar o template de certificado."
        )

    if request.method == "POST":
        form = CertificateTemplateForm(
            request.POST, request.FILES, instance=certificate_template
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Template atualizado com sucesso!")
            return redirect("certificate_template_list")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CertificateTemplateForm(instance=certificate_template)

    context = {"form": form, "object": certificate_template}

    template = loader.get_template("create_certificate_template.html")

    return HttpResponse(template.render(context=context, request=request))


@login_required
@teacher_only
def certificate_template_delete(request, pk):
    """Exclui um template de certificado"""
    template = CertificateTemplateModel.objects.filter(id=id, user=request.user)

    if not template:
        return HttpResponseNotFound(
            "Não foi possível localizar o template de certificado."
        )

    if request.method == "POST":
        template_name = template.name
        template.delete()
        messages.success(request, f'Template "{template_name}" excluído com sucesso!')
        return redirect("certificate_template_list")

    return render(
        request, "certificates/template_confirm_delete.html", {"object": template}
    )


@login_required
@teacher_only
def certificate_template_preview(request, pk):
    """Visualização de um template de certificado"""
    template = CertificateTemplateModel.objects.filter(id=id, user=request.user)

    if not template:
        return HttpResponseNotFound(
            "Não foi possível localizar o template de certificado."
        )

    # Dados de exemplo para o preview
    example_data = {
        "first_name": "João",
        "last_name": "Silva",
        "name": "Tech Conference 2024",
        "city": "São Paulo",
        "state": "SP",
        "country": "Brasil",
        "start_date": "15/03/2024",
        "end_date": "16/03/2024",
        "emitted_at": "17/03/2024",
        "user": request.user.get_full_name()
        or f"{request.user.first_name} {request.user.last_name}",
    }

    return render(
        request,
        "certificates/template_preview.html",
        {"object": template, "example_data": example_data},
    )


@login_required
@teacher_only
def certificate_template_quick_preview(request):
    """Preview rápido do template em desenvolvimento (AJAX)"""
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        html_content = request.POST.get("html_content", "")
        width = request.POST.get("width", 1200)
        height = request.POST.get("height", 800)

        # Substituir tags por valores de exemplo
        preview_content = html_content
        replacements = {
            "{{ first_name }}": "Maria",
            "{{ last_name }}": "Santos",
            "{{ name }}": "Workshop de Inovação",
            "{{ city }}": "Rio de Janeiro",
            "{{ state }}": "RJ",
            "{{ country }}": "Brasil",
            "{{ start_date }}": "20/04/2024",
            "{{ end_date }}": "21/04/2024",
            "{{ emitted_at }}": "22/04/2024",
            "{{ user }}": "Organizador Exemplo",
        }

        for tag, value in replacements.items():
            preview_content = preview_content.replace(tag, value)

        return JsonResponse(
            {"preview_content": preview_content, "width": width, "height": height}
        )

    return JsonResponse({"error": "Requisição inválida"}, status=400)


@login_required
@teacher_only
def certificate_template_duplicate(request, pk):
    """Duplica um template existente"""
    template = CertificateTemplateModel.objects.filter(id=id, user=request.user)

    if not template:
        return HttpResponseNotFound(
            "Não foi possível localizar o template de certificado."
        )

    if request.method == "POST":
        # Cria uma cópia do template
        new_template = CertificateTemplateModel(
            user=request.user,
            name=f"{template.name} (Cópia)",
            html_content=template.html_content,
            width=template.width,
            height=template.height,
        )

        new_template.save()
        messages.success(request, "Template duplicado com sucesso!")
        return redirect("certificate_template_list")

    return render(
        request, "certificates/template_duplicate_confirm.html", {"object": template}
    )


@login_required
@teacher_only
def certificate_template_use(request, pk, event_id):
    """Associa um template a um evento específico"""
    template = CertificateTemplateModel.objects.filter(id=id, user=request.user)

    if not template:
        return HttpResponseNotFound(
            "Não foi possível localizar o template de certificado."
        )
    # Aqui você precisaria do modelo Event - ajuste conforme sua aplicação
    # event = get_object_or_404(Event, pk=event_id, user=request.user)

    if request.method == "POST":
        # Lógica para associar o template ao evento
        # event.certificate_template = template
        # event.save()

        messages.success(
            request, f'Template "{template.name}" associado ao evento com sucesso!'
        )
        # return redirect('event_detail', pk=event_id)
        return redirect("certificate_template_list")

    return render(
        request,
        "certificates/template_use_confirm.html",
        {"object": template, "event_id": event_id},
    )
