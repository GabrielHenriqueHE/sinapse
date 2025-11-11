from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import UserModel
from apps.core.models import BaseModel


class CertificateTemplateModel(BaseModel):
    name: type[models.Field] = models.CharField(
        max_length=255, verbose_name=_("Nome do template"), null=False, blank=False
    )

    user: type[models.ForeignObject] = models.ForeignKey(
        UserModel,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_("Organizador"),
    )

    html_content: type[models.Field] = models.TextField(
        null=False, blank=False, verbose_name=_("Conteúdo HTML")
    )

    width: type[models.Field] = models.FloatField(
        null=False, blank=False, default=1200.00, verbose_name=_("Largura (px)")
    )

    height: type[models.Field] = models.FloatField(
        null=False, blank=False, default=800.00, verbose_name=_("Altura (px)")
    )

    class Meta:
        db_table = "tb_certificate_template"
        verbose_name = _("Template de certificado")
        verbose_name_plural = _("Templates de certificado")
