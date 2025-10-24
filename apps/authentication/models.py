from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Field
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class UserModel(AbstractUser, BaseModel):

    class Role(models.TextChoices):
        STUDENT = "STUDENT", _("Estudante")
        TEACHER = "TEACHER", _("Professor")

    username = None

    first_name: type[Field] = models.CharField(max_length=30, null=False)
    last_name: type[Field] = models.CharField(max_length=30, null=False)
    email: type[Field] = models.EmailField(max_length=254, unique=True, null=False)
    password: type[Field] = models.CharField(max_length=128, null=False)

    role: type[Field] = models.CharField(
        max_length=254, null=False, choices=Role.choices, default=Role.STUDENT
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    EMAIL_FIELD = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name", "password")

    class Meta:
        db_table = "tb_users"
        indexes = [models.Index(fields=["email"])]


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um usuário com o e-mail e senha fornecidos.
        """

        if not email:
            raise ValueError("O usuário deve ter um endereço de e-mail!")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e salva um superusuário com o email e senha fornecidos.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserModel.Role.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário deve ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário deve ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
