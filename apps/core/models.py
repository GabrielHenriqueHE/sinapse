import uuid

from django.db import models
from django.db.models import Field
from django.utils import timezone


class BaseModel(models.Model):
    id: type[Field] = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at: type[Field] = models.DateTimeField(null=False, auto_now_add=True)
    updated_at: type[Field] = models.DateTimeField(null=False, auto_now=True)
    deleted_at: type[Field] = models.DateTimeField(null=True)
    deleted: type[Field] = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted = True
        self.deleted_at = timezone.now()
