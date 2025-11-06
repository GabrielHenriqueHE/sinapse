from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import UserModel
from apps.core.models import BaseModel


class CategoryModel(BaseModel):
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
        verbose_name=_("Nome da categoria"),
    )

    class Meta:
        db_table = "tb_category"
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")

    def __str__(self):
        return self.name.capitalize()

    def clean(self):
        if self.name:
            self.name = self.name.strip().lower()
        super().clean()


class EventModel(BaseModel):

    class Status(models.TextChoices):
        OPEN = "OPEN", _("Aberto")
        CLOSED = "CLOSED", _("Fechado")
        FINISHED = "FINISHED", _("Finalizado")
        CANCELED = "CANCELED", _("Cancelado")

    name = models.CharField(
        max_length=100, null=False, blank=False, verbose_name=_("Nome do evento")
    )

    description = models.CharField(
        max_length=300, null=True, blank=True, verbose_name=_("Descrição")
    )

    topics = ArrayField(
        models.CharField(max_length=100, blank=False),
        blank=True,
        default=list,
        verbose_name=_("Tópicos"),
    )

    street = models.CharField(
        max_length=255, null=False, blank=False, verbose_name=_("Logradouro")
    )

    complement = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Complemento")
    )

    city = models.CharField(
        max_length=100, null=False, blank=False, verbose_name=_("Cidade")
    )

    state = models.CharField(
        max_length=100, null=False, blank=False, verbose_name=_("Estado")
    )

    country = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        default="Brasil",
        verbose_name=_("País"),
    )

    zip_code = models.CharField(
        max_length=20, null=False, blank=False, verbose_name=_("Código postal")
    )

    start_date = models.DateTimeField(
        null=False, blank=False, verbose_name=_("Data de início")
    )

    end_date = models.DateTimeField(
        null=False, blank=False, verbose_name=_("Data de término")
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_("Status"),
    )

    participants_limit = models.IntegerField(
        null=True, blank=True, verbose_name=_("Limite de participantes")
    )

    image_url = models.URLField(
        null=True, blank=True, max_length=500, verbose_name=_("URL da imagem")
    )

    category = models.ForeignKey(
        CategoryModel,
        related_name="events",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name=_("Categoria"),
    )

    user = models.ForeignKey(
        UserModel,
        related_name="created_events",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name=_("Criador do evento"),
    )

    participants = models.ManyToManyField(
        to=UserModel,
        through="EventParticipantModel",
        through_fields=("event", "user"),
        related_name="participated_events",
        verbose_name=_("Participantes"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tb_events"
        verbose_name = _("Evento")
        verbose_name_plural = _("Eventos")
        indexes = [
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(
                    _("A data de término deve ser posterior à data de início")
                )

            if self.start_date < timezone.now():
                raise ValidationError(_("A data de início não pode ser no passado"))

        if self.participants_limit and self.participants_limit < 1:
            raise ValidationError(
                _("O limite de participantes deve ser maior que zero")
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_full(self):
        if not self.participants_limit:
            return False
        return self.participants.count() >= self.participants_limit

    @property
    def available_spots(self):
        if not self.participants_limit:
            return None
        return max(0, self.participants_limit - self.participants.count())
    
    @property
    def attendance_available(self):
        return self.end_date < timezone.now()


class EventParticipantModel(BaseModel):

    class ParticipationStatus(models.TextChoices):
        PRESENT = "PRESENT", _("Presente")
        ABSENT = "ABSENT", _("Ausente")
        PENDING = "PENDING", _("Pendente")  # Novo status

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="event_participations",
        verbose_name=_("Usuário"),
    )

    event = models.ForeignKey(
        EventModel,
        on_delete=models.CASCADE,
        related_name="participants_records",
        verbose_name=_("Evento"),
    )

    status = models.CharField(
        max_length=20,
        choices=ParticipationStatus.choices,
        default=ParticipationStatus.PENDING,  # Valor padrão
        verbose_name=_("Status da participação"),
    )

    attended_at = models.DateTimeField(  # Novo campo para registrar quando a presença foi confirmada
        null=True, 
        blank=True,
        verbose_name=_("Data/hora da confirmação de presença")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tb_events_participants"
        unique_together = ["user", "event"]
        verbose_name = _("Participante do Evento")
        verbose_name_plural = _("Participantes dos Eventos")

    def __str__(self):
        return f"{self.user} - {self.event}"

    def clean(self):
        if self.event and self.user:
            if self.event.user == self.user:
                raise ValidationError(
                    _("O criador do evento não pode se inscrever como participante")
                )

    def save(self, *args, **kwargs):
        if self.status == self.ParticipationStatus.PRESENT and not self.attended_at:
            self.attended_at = timezone.now()
        elif self.status != self.ParticipationStatus.PRESENT:
            self.attended_at = None

        self.full_clean()
        super().save(*args, **kwargs)
