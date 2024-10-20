from django.db import models

from apps.fsm.models import Object


class Spend(models.Model):
    """Records of coins spent on objects"""
    user = models.UUIDField()
    object = models.IntegerField()
    fund = models.JSONField()
    spent_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.IntegerField()

    class Meta:
        ordering = ['-spent_at']

    def __str__(self):
        return f"{self.user} spent {self.fund} coins on {self.object}"
