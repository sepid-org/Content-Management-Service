from django.db import models


class Spend(models.Model):
    """Records of coins spent on objects by users."""
    user = models.UUIDField()
    object_id = models.IntegerField()
    fund = models.JSONField()
    spent_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.PositiveIntegerField()

    class Meta:
        ordering = ['-spent_at']

    def __str__(self):
        return f"{self.user} spent {self.fund} on object {self.object_id} at {self.spent_at}"
