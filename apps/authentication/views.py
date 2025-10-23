from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader

from apps.authentication.forms import CustomAuthenticationForm, CustomUserCreationForm


def landing_page(request):
    register_form = CustomUserCreationForm()
    login_form = CustomAuthenticationForm()

    context = {
        "register_form": register_form,
        "login_form": login_form,
    }

    template = loader.get_template("index.html")

    return HttpResponse(template.render(context=context, request=request))


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("events_index")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CustomUserCreationForm()

    context = {"register_form": form}

    template = loader.get_template("index.html")

    return HttpResponse(template.render(context=context, request=request))


def auth_login(request):
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
                messages.success(request, f"Bem-vindo de volta, {user.first_name}!")
                return redirect("events_index")
        else:
            messages.error(request, "Email ou senha inválidos.")

    context = {"login_form": form}

    template = loader.get_template("index.html")

    return HttpResponse(template.render(context=context, request=request))


@login_required(login_url="landing_page")
def logout_user(request):
    logout(request)
    return redirect("landing_page")
