
from django.db import models

from apps.fsm.models.form import RegistrationFormC, RegistrationForm


class Font(models.Model):
    font_file = models.FileField(upload_to='fonts/', blank=False)

    @property
    def name(self):
        return self.font_file.name if not self.font_file.name.startswith('fonts/') else self.font_file.name[6:]

    def __str__(self) -> str:
        return self.name


class CertificateTemplate(models.Model):
    # i.e. gold, silver, etc.
    certificate_type = models.CharField(max_length=50, null=True, blank=True)
    template_file = models.FileField(
        upload_to='certificate_templates/', null=True, blank=True)
    name_X_percentage = models.FloatField(null=True, blank=True, default=None)
    name_Y_percentage = models.FloatField(null=True, blank=True, default=None)
    registration_formc = models.ForeignKey(RegistrationFormC, on_delete=models.CASCADE,
                                          related_name='certificate_templates')
    registration_form = models.ForeignKey(RegistrationForm, on_delete=models.CASCADE,
                                           related_name='certificate_templates', null=True)

    font = models.ForeignKey(
        Font, on_delete=models.SET_NULL, related_name='templates', null=True)
    font_size = models.IntegerField(default=100)
