from typing import Dict
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel
from apps.accounts.models import Purchase, User
from rest_framework.exceptions import ParseError

from errors.error_codes import serialize_error
from apps.accounts.models import Purchase, User
from apps.fsm.models.base import Paper


class Form(Paper):
    class AudienceType(models.TextChoices):
        STUDENT = 'Student', 'Student'
        ACADEMIC = 'Academic', 'Academic'
        ALL = 'All', 'All'

    audience_type = models.CharField(
        max_length=50,
        choices=AudienceType.choices,
        default=AudienceType.ALL
    )
    background_image = models.URLField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    participant_limit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.id}: {self.paper_type}'


class RegistrationForm(Form):
    class AcceptingStatus(models.TextChoices):
        AutoAccept = 'AutoAccept'
        CorrectAccept = 'CorrectAccept'
        Manual = 'Manual'

    class GenderPartitionStatus(models.TextChoices):
        OnlyMale = 'OnlyMale'
        OnlyFemale = 'OnlyFemale'
        BothPartitioned = 'BothPartitioned'
        BothNonPartitioned = 'BothNonPartitioned'

    class RegisterPermissionStatus(models.TextChoices):
        DeadlineMissed = "DeadlineMissed"
        NotStarted = "NotStarted"
        StudentshipDataIncomplete = "StudentshipDataIncomplete"
        NotPermitted = "NotPermitted"
        GradeNotAvailable = "GradeNotAvailable"
        GradeNotSuitable = "GradeNotSuitable"
        StudentshipDataNotApproved = "StudentshipDataNotApproved"
        Permitted = "Permitted"
        NotRightGender = "NotRightGender"
        MaxRegistrantsReached = "MaxRegistrantsReached"
        AlreadyRegistered = "AlreadyRegistered"

    min_grade = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(12), MinValueValidator(0)]
    )
    max_grade = models.IntegerField(
        default=12,
        validators=[MaxValueValidator(12), MinValueValidator(0)]
    )

    accepting_status = models.CharField(
        max_length=15,
        default=AcceptingStatus.AutoAccept,
        choices=AcceptingStatus.choices
    )
    gender_partition_status = models.CharField(
        max_length=25,
        default=GenderPartitionStatus.BothPartitioned,
        choices=GenderPartitionStatus.choices
    )
    has_certificate = models.BooleanField(default=False)
    certificates_ready = models.BooleanField(default=False)

    max_registrants = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of registrants allowed. Null means no limit."
    )

    @property
    def registration_receipts(self) -> models.QuerySet['RegistrationReceipt']:
        return RegistrationReceipt.objects.filter(
            id__in=self.answer_sheets.values_list('id', flat=True)
        )

    @property
    def program_or_fsm(self):
        try:
            if self.program:
                return self.program
        except AttributeError:
            pass

        try:
            if self.fsm:
                return self.fsm
        except AttributeError:
            pass

        return None

    def get_user_registration_permission_status(self, user):
        """
        Determines whether a user is permitted to register for this form.
        Returns one of the RegisterPermissionStatus enum values based on the checks.
        """
        # 1. User must be authenticated
        if not user.is_authenticated:
            return self.RegisterPermissionStatus.NotPermitted

        already_registered = self._check_already_registered(user)
        if already_registered:
            return already_registered

        # 2. Check registration period (start/end dates)
        time_error = self._check_time()
        if time_error is not None:
            return time_error

        # 3. Check gender eligibility
        gender_error = self._check_gender(user)
        if gender_error is not None:
            return gender_error

        # 4. Check audience-specific rules
        if self.audience_type == self.AudienceType.ACADEMIC:
            audience_error = self._check_academic_audience(user)
            if audience_error is not None:
                return audience_error

        elif self.audience_type == self.AudienceType.STUDENT:
            audience_error = self._check_student_audience(user)
            if audience_error is not None:
                return audience_error

        # 5. Check maximum registrants capacity (for all audience types)
        capacity_error = self._check_capacity()
        if capacity_error is not None:
            return capacity_error

        # 6. If all checks pass, permit registration
        return self.RegisterPermissionStatus.Permitted

    def _check_time(self):
        """
        Returns a RegisterPermissionStatus value if registration is too early or too late.
        Otherwise, returns None.
        """
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return self.RegisterPermissionStatus.NotStarted
        if self.end_date and now > self.end_date:
            return self.RegisterPermissionStatus.DeadlineMissed
        return None

    def _check_gender(self, user):
        """
        Checks if user's gender matches the form's gender partition rules.
        Returns a RegisterPermissionStatus value on mismatch, otherwise None.
        """
        status = self.gender_partition_status
        user_gender = getattr(user, 'gender', None)
        if status == self.GenderPartitionStatus.OnlyFemale and user_gender == 'Male':
            return self.RegisterPermissionStatus.NotRightGender
        if status == self.GenderPartitionStatus.OnlyMale and user_gender == 'Female':
            return self.RegisterPermissionStatus.NotRightGender
        return None

    def _check_academic_audience(self, user):
        """
        Validates rules specific to 'Academic' audience_type.
        Returns a RegisterPermissionStatus value if there's any issue; otherwise, None.
        """
        studentship = getattr(user, 'academic_studentship', None)
        if not studentship:
            return self.RegisterPermissionStatus.StudentshipDataNotApproved
        if not studentship.university:
            return self.RegisterPermissionStatus.StudentshipDataIncomplete
        return None

    def _check_student_audience(self, user):
        """
        Validates rules specific to 'Student' audience_type.
        Returns a RegisterPermissionStatus value if there's any issue; otherwise, None.
        """
        studentship = getattr(user, 'school_studentship', None)
        if not studentship:
            return self.RegisterPermissionStatus.StudentshipDataNotApproved
        if not studentship.school:
            return self.RegisterPermissionStatus.StudentshipDataIncomplete
        if not studentship.grade:
            return self.RegisterPermissionStatus.GradeNotAvailable
        if not (self.min_grade <= studentship.grade <= self.max_grade):
            return self.RegisterPermissionStatus.GradeNotSuitable
        return None

    def _check_capacity(self):
        """
        Checks if the maximum number of registrants has been reached.
        Returns RegisterPermissionStatus.MaxRegistrantsReached if the limit is met,
        otherwise returns None.
        """
        if self.max_registrants is None:
            return None  # No capacity limit set

        current_count = self.registration_receipts.filter(
            is_participating=True).count()
        if current_count >= self.max_registrants:
            return self.RegisterPermissionStatus.MaxRegistrantsReached
        return None

    def _check_already_registered(self, user):
        if self.registration_receipts.filter(user=user).exists():
            return self.RegisterPermissionStatus.AlreadyRegistered
        return None

    def __str__(self):
        return f'<{self.id}-{getattr(self, "paper_type", "")}>: {self.program_or_fsm.name if self.program_or_fsm else None}'


class AnswerSheet(PolymorphicModel):
    class AnswerSheetType(models.TextChoices):
        RegistrationReceipt = "RegistrationReceipt"
        StateAnswerSheet = "StateAnswerSheet"
        General = "General"

    class CorrectionStatus(models.TextChoices):
        CORRECT = "Correct", "Correct"
        INCORRECT = "Wrong", "Incorrect"
        MANUAL_REVIEW_REQUIRED = "ManualCorrectionRequired", "Manual Review Required"
        NO_REVIEW_NEEDED = "NoCorrectionRequired", "No Review Needed"
        NO_SOLUTION_PROVIDED = "NoSolutionAvailable", "No Solution Provided"
        OTHER = "Other", "Other"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answer_sheet_type = models.CharField(
        max_length=25,
        default=AnswerSheetType.General,
        choices=AnswerSheetType.choices,
    )
    user = models.ForeignKey(
        User,
        related_name='answer_sheets',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # todo: should be move to RegistrationReceipt?:
    form = models.ForeignKey(
        Form,
        related_name='answer_sheets',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def assess(self) -> Dict[int, dict]:
        result: Dict[int, dict] = {}
        for answer in self.answers.filter(is_final_answer=True):
            result[answer.id] = answer.assess()
        return result

    def delete(self):
        self.answers.clear()
        return super(AnswerSheet, self).delete()

    class Meta:
        indexes = [
            # in case you do AnswerSheet.objects.filter(user=…)
            models.Index(fields=["user"], name="idx_sheet_user"),
            # for lookups like AnswerSheet.objects.filter(user=…, form=…)
            models.Index(fields=['user', 'form'], name='idx_sheet_user_form'),
        ]


class RegistrationReceipt(AnswerSheet):
    class RegistrationStatus(models.TextChoices):
        Accepted = "Accepted"
        Rejected = "Rejected"
        Waiting = "Waiting"

    status = models.CharField(max_length=25, blank=False,
                              default='Waiting', choices=RegistrationStatus.choices)
    is_participating = models.BooleanField(default=False)
    certificate = models.FileField(
        upload_to='certificates/', null=True, blank=True, default=None)
    team = models.ForeignKey('fsm.Team', on_delete=models.SET_NULL,
                             related_name='members', null=True, blank=True)

    @property
    def purchases(self):
        purchases = []
        merchandises = self.form.program.merchandises
        if merchandises:
            for merchandise in merchandises:
                purchases.append(*merchandise.purchases.filter(user=self.user))
            return purchases
        return Purchase.objects.none()

    @property
    def is_paid(self):
        return len(self.purchases.filter(
            status=Purchase.Status.Success)) > 0 if self.form.program_or_fsm.merchandise else True

    def get_player_of(self, fsm):
        return self.players.filter(fsm=fsm).first()

    def correction_status(self):
        from apps.fsm.models.response import MultiChoiceAnswer, SmallAnswer
        for a in self.answers.all():
            if isinstance(a, (SmallAnswer, MultiChoiceAnswer)):
                correction_status = a.correction_status()
                if correction_status == self.CorrectionStatus.Wrong:
                    return self.CorrectionStatus.Wrong
                elif correction_status != self.CorrectionStatus.Correct:
                    return self.CorrectionStatus.NoCorrectionRequired
            else:
                return self.CorrectionStatus.ManualCorrectionRequired
        return self.CorrectionStatus.Correct

    def register_in_form(self, registration_form):
        program = registration_form.program
        if not program:
            return
        if program.maximum_participant is None or len(program.final_participants) < program.maximum_participant:
            if registration_form.accepting_status == RegistrationForm.AcceptingStatus.AutoAccept:
                self.status = RegistrationReceipt.RegistrationStatus.Accepted
                if program.is_free:
                    self.is_participating = True
                self.save()
            elif registration_form.accepting_status == RegistrationForm.AcceptingStatus.CorrectAccept:
                if self.correction_status() == RegistrationReceipt.CorrectionStatus.Correct:
                    self.status = RegistrationReceipt.RegistrationStatus.Accepted
                    if program.is_free:
                        self.is_participating = True
                    self.save()
        else:
            self.status = RegistrationReceipt.RegistrationStatus.Rejected
            self.save()
            raise ParseError(serialize_error('4035'))

    def __str__(self):
        return f'{self.id}:{self.user.full_name}{"+" if self.is_participating else "x"}'

    class Meta:
        indexes = [
            # for filtering by participation flag
            models.Index(fields=['is_participating'],
                         name='idx_rr_participating'),
        ]
