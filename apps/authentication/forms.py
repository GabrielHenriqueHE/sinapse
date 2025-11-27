from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from apps.authentication.models import UserModel


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm",
                "placeholder": "Seu nome",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm",
                "placeholder": "Seu sobrenome",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm",
                "placeholder": "seu@email.com",
            }
        ),
    )

    # NOVO CAMPO: Tipo de conta
    role = forms.ChoiceField(
        choices=UserModel.Role.choices,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                "class": "h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300",
            }
        ),
        initial=UserModel.Role.STUDENT,
        label="Tipo de Conta"
    )

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm",
                "placeholder": "Crie uma senha",
            }
        ),
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm",
                "placeholder": "Confirme sua senha",
            }
        ),
    )

    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            }
        ),
        error_messages={"required": "Você deve aceitar os termos de serviço."},
    )

    class Meta:
        model = UserModel
        fields = ("first_name", "last_name", "email", "role", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover a ajuda padrão de senha do Django (opcional)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm",
                "placeholder": "seu@email.com",
                "autocomplete": "email",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm",
                "placeholder": "Sua senha",
                "autocomplete": "current-password",
            }
        )
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            }
        ),
    )

    class Meta:
        model = UserModel