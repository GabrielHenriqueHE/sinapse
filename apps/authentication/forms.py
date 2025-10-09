from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import UserModel


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                "placeholder": "Seu nome",
                "id": "form-create-account-first-name-input",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                "placeholder": "Seu sobrenome",
                "id": "form-create-account-last-name-input",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                "placeholder": "seu@email.com",
                "id": "form-create-account-email-input",
            }
        ),
    )

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                "placeholder": "Crie uma senha",
                "id": "form-create-account-password-input",
            }
        ),
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                "placeholder": "Confirme sua senha",
                "id": "form-create-account-confirm-password-input",
            }
        ),
    )

    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={"class": "rounded border-gray-300 text-black focus:ring-black mt-1"}
        ),
        error_messages={"required": "Você deve aceitar os termos de serviço."},
    )

    class Meta:
        model = UserModel
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                "placeholder": "seu@email.com",
                "autocomplete": "email",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "font-mono w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition duration-300",
                "placeholder": "Sua senha",
                "autocomplete": "current-password",
            }
        )
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "rounded border-gray-300 text-black focus:ring-black"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
