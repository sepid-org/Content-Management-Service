from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import QuerySet
from datetime import datetime
from polymorphic.models import PolymorphicModel
from apps.accounts.models import Purchase, User
from rest_framework.exceptions import ParseError, PermissionDenied

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
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

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

    class AudienceType(models.TextChoices):
        Student = 'Student'
        Academic = 'Academic'
        All = 'All'

    min_grade = models.IntegerField(
        default=0, validators=[MaxValueValidator(12), MinValueValidator(0)])
    max_grade = models.IntegerField(
        default=12, validators=[MaxValueValidator(12), MinValueValidator(0)])

    accepting_status = models.CharField(
        max_length=15, default='AutoAccept', choices=AcceptingStatus.choices)
    gender_partition_status = models.CharField(max_length=25, default='BothPartitioned',
                                               choices=GenderPartitionStatus.choices)
    has_certificate = models.BooleanField(default=False)
    certificates_ready = models.BooleanField(default=False)

    @property
    def registration_receipts(self) -> QuerySet['RegistrationReceipt']:
        return RegistrationReceipt.objects.filter(
            id__in=self.answer_sheets.values_list('id', flat=True)
        )

    @property
    def program_or_fsm(self):
        try:
            if self.program:
                return self.program
        except:
            try:
                if self.fsm:
                    return self.fsm
            except:
                return None

    def get_user_registration_permission_status(self, user):
        if user.is_authenticated == False:
            return self.RegisterPermissionStatus.NotPermitted

        time_check_result = self.check_time()
        if time_check_result != 'ok':
            return time_check_result

        gender_check_result = self.check_gender(user)
        if gender_check_result != 'ok':
            return gender_check_result

        # remove different types of audiences. the program manager should build the registration path him/her self.
        if self.audience_type == self.AudienceType.Academic:
            studentship = user.academic_studentship
            if studentship:
                if not studentship.university:
                    return self.RegisterPermissionStatus.StudentshipDataIncomplete
            else:
                return self.RegisterPermissionStatus.StudentshipDataNotApproved

        if self.audience_type == self.AudienceType.Student:
            studentship = user.school_studentship
            if not studentship:
                return self.RegisterPermissionStatus.StudentshipDataNotApproved
            if not studentship.grade:
                return self.RegisterPermissionStatus.GradeNotAvailable
            if not studentship.school:
                return self.RegisterPermissionStatus.StudentshipDataIncomplete
            if self.min_grade > studentship.grade or studentship.grade > self.max_grade:
                return self.RegisterPermissionStatus.GradeNotSuitable
            return self.RegisterPermissionStatus.Permitted

        return self.RegisterPermissionStatus.Permitted

    def validate_user_registration_permission_status(self, user):
        register_permission_status = self.get_user_registration_permission_status(
            user)
        if register_permission_status == RegistrationForm.RegisterPermissionStatus.DeadlineMissed:
            raise ParseError(serialize_error('4036'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.NotStarted:
            raise ParseError(serialize_error('4100'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.StudentshipDataIncomplete:
            raise PermissionDenied(serialize_error('4057'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.NotPermitted:
            raise PermissionDenied(serialize_error('4032'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.GradeNotAvailable:
            raise ParseError(serialize_error('4033'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.GradeNotSuitable:
            raise ParseError(serialize_error('6004'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.StudentshipDataNotApproved:
            raise ParseError(serialize_error('4034'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.NotRightGender:
            raise ParseError(serialize_error('4109'))
        elif register_permission_status == RegistrationForm.RegisterPermissionStatus.Permitted:
            # its ok
            pass

    def check_time(self):
        if self.end_date and datetime.now(self.end_date.tzinfo) > self.end_date:
            return self.RegisterPermissionStatus.DeadlineMissed
        if self.start_date and datetime.now(self.end_date.tzinfo) < self.start_date:
            return self.RegisterPermissionStatus.NotStarted
        return 'ok'

    def check_gender(self, user):
        if (self.gender_partition_status == 'OnlyFemale' and user.gender == 'Male') or \
                (self.gender_partition_status == 'OnlyMale' and user.gender == 'Female'):
            return self.RegisterPermissionStatus.NotRightGender
        return 'ok'

    def __str__(self):
        return f'<{self.id}-{self.paper_type}>:{self.program_or_fsm.name if self.program_or_fsm else None}'


class AnswerSheet(PolymorphicModel):
    class AnswerSheetType(models.TextChoices):
        RegistrationReceipt = "RegistrationReceipt"
        StateAnswerSheet = "StateAnswerSheet"
        General = "General"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    answer_sheet_type = models.CharField(
        max_length=25, default=AnswerSheetType.General, choices=AnswerSheetType.choices)
    user = models.ForeignKey(
        User,
        related_name='answer_sheets',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    form = models.ForeignKey(
        Form, related_name='answer_sheets', on_delete=models.PROTECT)

    def delete(self):
        self.answers.clear()
        return super(AnswerSheet, self).delete()


class RegistrationReceipt(AnswerSheet):
    class RegistrationStatus(models.TextChoices):
        Accepted = "Accepted"
        Rejected = "Rejected"
        Waiting = "Waiting"

    class CorrectionStatus(models.TextChoices):
        Correct = "Correct"
        Wrong = "Wrong"
        ManualCorrectionRequired = "ManualCorrectionRequired"
        NoCorrectionRequired = "NoCorrectionRequired"
        NoSolutionAvailable = "NoSolutionAvailable"
        Other = "Other"

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
