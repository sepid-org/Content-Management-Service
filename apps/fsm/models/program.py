from django.db import models
from apps.accounts.models import User
from apps.fsm.models.form import RegistrationForm


class Program(models.Model):
    class ProgramType(models.TextChoices):
        EVENT = "Event"
        CLASS = "Class"
        CAMPAIGN = "Campaign"
        GAME = "Game"
        COURSE = "Course"

    class ParticipationType(models.TextChoices):
        TEAM = "Team"
        INDIVIDUAL = "Individual"

    type = models.CharField(
        max_length=40,
        choices=ProgramType.choices,
        default=ProgramType.EVENT
    )

    participation_type = models.CharField(
        max_length=40,
        choices=ParticipationType.choices,
        default=ParticipationType.INDIVIDUAL
    )

    slug = models.SlugField(max_length=100, unique=True, db_index=True,  null=True,
                            blank=True, help_text="Unique identifier for the program")

    admins = models.ManyToManyField(
        User, related_name='administered_programs', null=True, blank=True)

    website = models.CharField(blank=True, null=True, max_length=50)

    registration_form = models.OneToOneField(
        RegistrationForm, related_name='program', on_delete=models.SET_NULL, null=True)

    creator = models.ForeignKey('accounts.User', related_name='programs', on_delete=models.SET_NULL, null=True,
                                blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_image = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    team_size = models.IntegerField(null=True, blank=True)
    maximum_participant = models.IntegerField(null=True, blank=True)
    accessible_after_closure = models.BooleanField(default=False)
    show_scores = models.BooleanField(default=False)
    site_help_paper_id = models.IntegerField(blank=True, null=True)
    FAQs_paper_id = models.IntegerField(blank=True, null=True)
    program_contact_info = models.OneToOneField(
        'ProgramContactInfo', on_delete=models.SET_NULL, related_name='program', blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=False)

    menu = models.ForeignKey(
        to='fsm.FSM',
        related_name='menu_program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.id
        super().save(*args, **kwargs)

    @property
    def modifiers(self):
        modifiers = {self.creator} if self.creator is not None else set()
        modifiers |= set(self.admins.all())
        return modifiers

    @property
    def is_free(self):
        if len(self.merchandises.filter(is_active=True)) == 0:
            return True
        return False

    @property
    def initial_participants(self):
        return self.registration_form.registration_receipts.all()

    @property
    def final_participants(self):
        return self.registration_form.registration_receipts.filter(is_participating=True)

    def delete(self, using=None, keep_parents=False):
        self.registration_form.delete() if self.registration_form is not None else None
        return super(Program, self).delete(using, keep_parents)

    class Meta:
        ordering = ['-id']


class ProgramContactInfo(models.Model):
    telegram_link = models.URLField(max_length=100, null=True, blank=True)
    shad_link = models.URLField(max_length=100, null=True, blank=True)
    eitaa_link = models.URLField(max_length=100, null=True, blank=True)
    bale_link = models.URLField(max_length=100, null=True, blank=True)
    instagram_link = models.URLField(max_length=100, null=True, blank=True)
    rubika_link = models.URLField(max_length=100, null=True, blank=True)
    whatsapp_link = models.URLField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
