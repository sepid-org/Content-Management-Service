import uuid
from django.db import models


class File(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='files/')

    def __str__(self) -> str:
        return {self.name}
