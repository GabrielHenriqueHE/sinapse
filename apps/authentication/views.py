from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader

from apps.authentication.forms import CustomAuthenticationForm, CustomUserCreationForm


def landing_page(request):
    """Página inicial da aplicação"""
    if request.user.is_authenticated:
        return redirect("events_index")

    template = loader.get_template("index.html")
    return HttpResponse(template.render(request=request))


def register(request):
    """View para cadastro de novos usuários"""
    if request.user.is_authenticated:
        return redirect("events_index")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Mensagem personalizada baseada no tipo de conta
            if user.role == "TEACHER":
                messages.success(
                    request,
                    "Cadastro realizado com sucesso! Agora você pode criar e gerenciar eventos.",
                )
            else:
                messages.success(
                    request,
                    "Cadastro realizado com sucesso! Agora você pode participar de eventos.",
                )

            return redirect("events_index")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CustomUserCreationForm()

    context = {"form": form}
    template = loader.get_template("register.html")
    return HttpResponse(template.render(context=context, request=request))


def auth_login(request):
    """View para autenticação de usuários"""
    if request.user.is_authenticated:
        return redirect("events_index")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                remember_me = form.cleaned_data.get("remember_me")
                if not remember_me:
                    request.session.set_expiry(0)

                # Mensagem personalizada baseada no tipo de conta
                if user.role == "TEACHER":
                    messages.success(
                        request, f"Bem-vindo de volta, Professor {user.first_name}!"
                    )
                else:
                    messages.success(request, f"Bem-vindo de volta, {user.first_name}!")

                return redirect("events_index")
        else:
            messages.error(request, "Email ou senha inválidos.")
    else:
        form = CustomAuthenticationForm()

    context = {"form": form}
    template = loader.get_template("login.html")
    return HttpResponse(template.render(context=context, request=request))


@login_required(login_url="landing_page")
def logout_user(request):
    """View para logout de usuários"""
    logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect("landing_page")
