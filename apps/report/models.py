from django.db import models


class Excel_Export_Date(models.Model):
    Date = models.DateField(auto_now=True)
    name = models.CharField(max_length=256)

