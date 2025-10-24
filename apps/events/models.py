from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import UserModel
from apps.core.models import BaseModel


class CategoryModel(BaseModel):
    name = models.CharField(null=False, max_length=100)

    class Meta:
        db_table = "tb_category"

    def __str__(self):
        return self.name.capitalize()


class EventModel(BaseModel):

    class Status(models.TextChoices):
        OPEN = "OPEN", _("Aberto")
        CLOSED = "CLOSED", _("Fechado")
        FINISHED = "FINISHED", _("Finalizado")
        CANCELED = "CANCELED", _("Cancelado")

    name = models.CharField(
        max_length=100, null=False, verbose_name=_("Nome do evento")
    )

    description = models.CharField(
        max_length=300, null=True, verbose_name=_("Descrição")
    )

    topics = ArrayField(
        models.CharField(max_length=100, blank=False), verbose_name=_("Tópicos")
    )

    street = models.CharField(max_length=255, null=False, verbose_name=_("Logradouro"))

    complement = models.CharField(
        max_length=100, null=True, verbose_name=_("Complemento")
    )

    city = models.CharField(max_length=100, null=False, verbose_name=_("Cidade"))

    state = models.CharField(max_length=100, null=False, verbose_name=_("Estado"))

    country = models.CharField(max_length=100, null=False, verbose_name=_("País"))

    zip_code = models.CharField(
        max_length=8, null=False, verbose_name=_("Código postal")
    )

    start_date = models.DateTimeField(null=False, verbose_name=_("Data de início"))
    end_date = models.DateTimeField(null=False, verbose_name=_("Data de término"))

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )

    participants_limit = models.IntegerField(
        null=True, verbose_name=_("Limite de participantes")
    )

    image_url = models.CharField(
        null=True, max_length=500, verbose_name=_("URL da imagem")
    )

    category = models.ForeignKey(
        CategoryModel,
        related_name="events",
        on_delete=models.CASCADE,
        null=False,
        verbose_name=_("Categoria"),
    )

    user = models.ForeignKey(
        UserModel,
        related_name="created_events",
        on_delete=models.CASCADE,
        null=False,
        verbose_name=_("Usuário"),
    )

    participants = models.ManyToManyField(
        to=UserModel,
        through="EventParticipantModel",
        through_fields=("event", "user"),
        related_name="participated_events",
    )

    class Meta:
        db_table = "tb_events"

    def __str__(self):
        return self.name


class EventParticipantModel(BaseModel):
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="event_participations"
    )
    event = models.ForeignKey(
        EventModel, on_delete=models.CASCADE, related_name="event_participants"
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", _("Pendente")),
            ("CONFIRMED", _("Confirmado")),
            ("CANCELLED", _("Cancelado")),
        ],
        default="PENDING",
    )

    class Meta:
        db_table = "tb_events_participants"
        unique_together = ["user", "event"]
        verbose_name = _("Event Participant")
        verbose_name_plural = _("Event Participants")

    def __str__(self):
        return f"{self.user} - {self.event}"
