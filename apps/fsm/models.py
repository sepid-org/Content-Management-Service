from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save
import json
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from datetime import datetime
from polymorphic.models import PolymorphicModel
from abc import abstractmethod
from apps.accounts.models import Purchase, User

from apps.attributes.models import Attribute, IntrinsicAttribute, PerformableAction


################ BASE #################

def clone_paper(paper, *args, **kwargs):
    paper_type = paper.__class__
    model_fields = [
        field.name for field in paper_type._meta.get_fields() if field.name != 'id']
    dicted_model = {name: value for name, value
                    in paper.__dict__.items() if name in model_fields}
    cloned_paper = paper_type(
        **{**dicted_model,
           **kwargs,
           },
    )
    cloned_paper.save()
    return cloned_paper


class Paper(PolymorphicModel):
    class PaperType(models.TextChoices):
        RegistrationForm = 'RegistrationForm'
        State = 'State'
        Hint = 'Hint'
        WidgetHint = 'WidgetHint'
        Article = 'Article'
        General = 'General'

    paper_type = models.CharField(
        max_length=25, blank=False, choices=PaperType.choices)
    creator = models.ForeignKey('accounts.User', related_name='papers', null=True, blank=True,
                                on_delete=models.SET_NULL)
    since = models.DateTimeField(null=True, blank=True)
    till = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, default=None)
    is_exam = models.BooleanField(default=False)

    def delete(self):
        for w in Widget.objects.filter(paper=self):
            try:
                w.delete()
            except:
                w.paper = None
                w.save()
        return super(Paper, self).delete()

    def is_user_permitted(self, user: User):
        # if self.criteria:
        #     return self.criteria.evaluate(user)
        return True

    def __str__(self):
        return f"{self.paper_type}"


class Hint(Paper):
    reference = models.ForeignKey(
        'fsm.State', on_delete=models.CASCADE, related_name='hints')

    def clone(self, paper):
        return clone_hint(self, paper)


################ GROUP #################


class TeamManager(models.Manager):

    def get_team_from_widget(self, user, widget):
        program = widget.paper.fsm.program
        return Team.objects.filter(program=program, members__user=user).first()

    def get_teammates_from_widget(self, user, widget):
        team = self.get_team_from_widget(user, widget)
        return team.members.values_list('user', flat=True) if team is not None else [user]


class Team(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    program = models.ForeignKey(
        'fsm.Program', related_name='teams', on_delete=models.CASCADE)
    team_head = models.OneToOneField('RegistrationReceipt', related_name='headed_team', null=True, blank=True,
                                     on_delete=models.SET_NULL)

    chat_room = models.CharField(max_length=200, null=True, blank=True)

    objects = TeamManager()

    def __str__(self):
        return f'{self.name}:{",".join(member.user.full_name for member in self.members.all())}'


class Invitation(models.Model):
    class InvitationStatus(models.TextChoices):
        Waiting = "Waiting"
        Rejected = "Rejected"
        Accepted = "Accepted"

    invitee = models.ForeignKey(
        'RegistrationReceipt', on_delete=models.CASCADE, related_name='invitations')
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='team_members')
    status = models.CharField(
        max_length=15, default=InvitationStatus.Waiting, choices=InvitationStatus.choices)

    # class Meta:
    #     unique_together = ('invitee', 'team')


################ COURSE #################


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

    slug = models.SlugField(max_length=100, unique=True, null=True,
                            blank=True, help_text="Unique identifier for the program")

    admins = models.ManyToManyField(
        User, related_name='administered_programs', null=True, blank=True)

    website = models.CharField(blank=True, null=True, max_length=50)

    registration_form = models.OneToOneField(
        'fsm.RegistrationForm', related_name='program', on_delete=models.PROTECT)
    creator = models.ForeignKey('accounts.User', related_name='programs', on_delete=models.SET_NULL, null=True,
                                blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.URLField(null=True, blank=True)
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
        return self.registration_form.registration_receipts.filter()

    @property
    def final_participants(self):
        return self.registration_form.registration_receipts.filter(is_participating=True)

    def delete(self, using=None, keep_parents=False):
        self.registration_form.delete() if self.registration_form is not None else None
        return super(Program, self).delete(using, keep_parents)

    class Meta:
        ordering = ['-id']


class ProgramContactInfo(models.Model):
    telegram_link = models.CharField(
        max_length=100, null=True, blank=True)
    shad_link = models.CharField(max_length=100, null=True, blank=True)
    eitaa_link = models.CharField(max_length=100, null=True, blank=True)
    bale_link = models.CharField(max_length=100, null=True, blank=True)
    instagram_link = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)

################ FSM #################


class Content():

    @property
    def solve_reward(self):
        return self._get_performable_action_intrinsic_attribute_template_method('solve', 'reward')

    @property
    def solve_cost(self):
        return self._get_performable_action_intrinsic_attribute_template_method('solve', 'cost')

    @property
    def submission_cost(self):
        return self._get_performable_action_intrinsic_attribute_template_method('submit', 'cost')

    @property
    def submission_cost(self):
        return self._get_performable_action_intrinsic_attribute_template_method('submit', 'cost')

    @property
    def has_transition_lock(self):
        return bool(self.transition_lock)

    @property
    def transition_lock(self):
        return self._get_performable_action_intrinsic_attribute_template_method('transit', 'password')

    @property
    def has_entrance_lock(self):
        return bool(self.entrance_lock)

    @property
    def entrance_lock(self):
        return self._get_performable_action_intrinsic_attribute_template_method('enter', 'password')

    def _get_performable_action_intrinsic_attribute_template_method(self, performable_action_type, intrinsic_attribute_type):
        for performable_action in self._get_performable_actions():
            if performable_action.type == performable_action_type:
                for intrinsic_attribute in performable_action.attributes.all():
                    if intrinsic_attribute.type == intrinsic_attribute_type:
                        return intrinsic_attribute.value
        return None

    def _get_intrinsic_attributes(self) -> list[IntrinsicAttribute]:
        result = []
        for attribute in self.attributes.all():
            if isinstance(attribute, IntrinsicAttribute):
                result.append(attribute)
        return result

    def _get_performable_actions(self) -> list[PerformableAction]:
        result = []
        for attribute in self.attributes.all():
            if isinstance(attribute, PerformableAction):
                result.append(attribute)
        return result


class FSMManager(models.Manager):
    @transaction.atomic
    def create(self, **args):
        fsm = super().create(**args)
        fsm.mentors.add(fsm.creator)
        fsm.save()
        return fsm


class FSM(models.Model, Content):
    class FSMLearningType(models.TextChoices):
        Supervised = 'Supervised'
        Unsupervised = 'Unsupervised'

    class FSMPType(models.TextChoices):
        Team = 'Team'
        Individual = 'Individual'
        Hybrid = 'Hybrid'

    is_public = models.BooleanField(default=False)

    attributes = models.ManyToManyField(to=Attribute, null=True, blank=True)

    website = models.CharField(blank=True, null=True, max_length=50)

    program = models.ForeignKey(Program, on_delete=models.SET_NULL, related_name='fsms', default=None, null=True,
                                blank=True)
    registration_form = models.OneToOneField('fsm.RegistrationForm', related_name='fsm', on_delete=models.SET_NULL, null=True,
                                             blank=True)
    creator = models.ForeignKey('accounts.User', related_name='created_fsms', on_delete=models.SET_NULL, null=True,
                                blank=True)
    mentors = models.ManyToManyField(
        'accounts.User', related_name='fsms', blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_page = models.URLField()
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    first_state = models.OneToOneField('fsm.State', null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name='my_fsm')
    fsm_learning_type = models.CharField(max_length=40, default=FSMLearningType.Unsupervised,
                                         choices=FSMLearningType.choices)
    fsm_p_type = models.CharField(
        max_length=40, default=FSMPType.Individual, choices=FSMPType.choices)
    team_size = models.IntegerField(default=3)
    order_in_program = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = FSMManager()

    def __str__(self):
        return self.name

    @transaction.atomic
    def clone(self):
        cloned_fsm = FSM(
            name=self.name,
            description=self.description,
            cover_page=self.cover_page,
            is_active=self.is_active,
            fsm_learning_type=self.fsm_learning_type,
            fsm_p_type=self.fsm_p_type,
            team_size=self.team_size,
        )

        cloned_states = {}
        cloned_fsm.save()
        for tail_state in self.states.all():
            for outward_edge in tail_state.outward_edges.all():
                if tail_state.id not in cloned_states:
                    cloned_states[tail_state.id] = tail_state.clone(cloned_fsm)

                head_state = outward_edge.head
                if head_state.id not in cloned_states:
                    cloned_states[head_state.id] = head_state.clone(cloned_fsm)

                cloned_outward_edge = outward_edge.clone(cloned_states[tail_state.id],
                                                         cloned_states[head_state.id])

        cloned_fsm.first_state = cloned_states[self.first_state.id]
        cloned_fsm.save()

    def get_fsm(fsm_id: int):
        return FSM.objects.filter(id=fsm_id).first()


class Player(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    user = models.ForeignKey(
        User, related_name='players', on_delete=models.CASCADE)
    fsm = models.ForeignKey(FSM, related_name='players',
                            on_delete=models.CASCADE)

    receipt = models.ForeignKey(
        'fsm.RegistrationReceipt', related_name='players', on_delete=models.CASCADE)

    current_state = models.ForeignKey('fsm.State', null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='players')
    last_visit = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def team(self):
        return self.receipt.team if self.receipt else None

    @staticmethod
    def get_player(player_id: int):
        return Player.objects.filter(id=player_id).first()

    class Meta:
        unique_together = ('user', 'fsm', 'receipt')

    def __str__(self):
        return f'{self.user.full_name} in {self.fsm.name}'


class State(Paper):
    class StateTemplate(models.TextChoices):
        normal = 'normal'
        board = 'board'

    name = models.TextField(null=True, blank=True)
    fsm = models.ForeignKey(
        FSM, on_delete=models.CASCADE, related_name='states')
    template = models.CharField(max_length=20, default=StateTemplate.normal,
                                choices=StateTemplate.choices)

    @transaction.atomic
    def delete(self):
        try:
            if self.my_fsm:
                fsm = self.fsm
                fsm.first_state = fsm.states.exclude(id=self.id).first()
                fsm.save()
        except:
            pass
        return super(State, self).delete()

    def clone(self, fsm):
        cloned_state = clone_paper(self, fsm=fsm)
        cloned_widgets = [widget.clone(cloned_state)
                          for widget in self.widgets.all()]
        cloned_hints = [hint.clone(cloned_state) for hint in self.hints.all()]
        return cloned_state

    def __str__(self):
        return f'گام: {self.name} | کارگاه: {str(self.fsm)}'


class Edge(models.Model, Content):
    attributes = models.ManyToManyField(to=Attribute, null=True, blank=True)

    tail = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='inward_edges')
    is_back_enabled = models.BooleanField(default=True)
    priority = models.IntegerField(null=True, blank=True)
    is_visible = models.BooleanField(default=False)
    text = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('tail', 'head')

    @property
    def fsm(self):
        return self.head.fsm

    def clone(self, tail, head):
        cloned_edge = Edge(
            tail=tail,
            head=head,
            is_back_enabled=self.is_back_enabled,
            is_visible=self.is_visible,
        )
        cloned_edge.save()
        return cloned_edge

    def __str__(self):
        return f'از {self.tail.name} به {self.head.name}'


class PlayerTransition(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, related_name='player_transitions')
    source_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, related_name='player_departure_transitions')
    target_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, related_name='player_arrival_transitions')
    time = models.DateTimeField(null=True)
    transited_edge = models.ForeignKey(
        Edge, related_name='player_transitions', null=True, on_delete=models.SET_NULL)

    def is_edge_transited_in_reverse(self):
        return True  # todo: fix


class PlayerStateHistory(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, related_name='player_state_histories')
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, related_name='player_state_histories')
    arrival = models.ForeignKey(
        PlayerTransition, on_delete=models.SET_NULL, null=True, related_name='player_target_state_history')
    departure = models.ForeignKey(
        PlayerTransition, on_delete=models.SET_NULL, null=True, related_name='player_source_state_history')

    def __str__(self):
        return f'{self.player} - {self.state.name if self.state else "DELETED"}'


################ ARTICLE #################


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Article(Paper):
    website = models.CharField(blank=True, null=True, max_length=50)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_page = models.ImageField(
        upload_to='workshop/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles')
    is_draft = models.BooleanField(default=True)
    publisher = models.ForeignKey('accounts.EducationalInstitute', related_name='articles', on_delete=models.SET_NULL,
                                  null=True, blank=True)

############ FORM / RECEIPT ############


class AnswerSheet(PolymorphicModel):
    class AnswerSheetType(models.TextChoices):
        RegistrationReceipt = "RegistrationReceipt"
        StateAnswerSheet = "StateAnswerSheet"

    answer_sheet_type = models.CharField(
        max_length=25, blank=False, choices=AnswerSheetType.choices)

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

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    form = models.ForeignKey(
        'fsm.RegistrationForm', related_name='registration_receipts', on_delete=models.PROTECT)
    user = models.ForeignKey(
        'accounts.User', related_name='registration_receipts', on_delete=models.CASCADE)
    status = models.CharField(max_length=25, blank=False,
                              default='Waiting', choices=RegistrationStatus.choices)
    is_participating = models.BooleanField(default=False)
    certificate = models.FileField(
        upload_to='certificates/', null=True, blank=True, default=None)

    team = models.ForeignKey('fsm.Team', on_delete=models.SET_NULL,
                             related_name='members', null=True, blank=True)

    def get_player_of(self, fsm: FSM):
        return self.players.filter(fsm=fsm).first()

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

    class Meta:
        unique_together = ('form', 'user')

    def correction_status(self):
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

    def __str__(self):
        return f'{self.id}:{self.user.full_name}{"+" if self.is_participating else "x"}'


class RegistrationForm(Paper):
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
    audience_type = models.CharField(
        max_length=50, default='Student', choices=AudienceType.choices)

    has_certificate = models.BooleanField(default=False)
    certificates_ready = models.BooleanField(default=False)

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

    def get_user_permission_status(self, user):
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

    def check_time(self):
        if self.till and datetime.now(self.till.tzinfo) > self.till:
            return self.RegisterPermissionStatus.DeadlineMissed
        if self.since and datetime.now(self.since.tzinfo) < self.since:
            return self.RegisterPermissionStatus.NotStarted
        return 'ok'

    def check_gender(self, user):
        if (self.gender_partition_status == 'OnlyFemale' and user.gender == 'Male') or \
                (self.gender_partition_status == 'OnlyMale' and user.gender == 'Female'):
            return self.RegisterPermissionStatus.NotRightGender
        return 'ok'

    def __str__(self):
        return f'<{self.id}-{self.paper_type}>:{self.program_or_fsm.name if self.program_or_fsm else None}'


############ Widget ############


class Widget(PolymorphicModel, Content):
    class WidgetTypes(models.TextChoices):
        Iframe = 'Iframe'
        Video = 'Video'
        Image = 'Image'
        Aparat = 'Aparat'
        Audio = 'Audio'
        TextWidget = 'TextWidget'
        DetailBoxWidget = 'DetailBoxWidget'
        SmallAnswerProblem = 'SmallAnswerProblem'
        BigAnswerProblem = 'BigAnswerProblem'
        MultiChoiceProblem = 'MultiChoiceProblem'
        UploadFileProblem = 'UploadFileProblem'

    widget_type = models.CharField(max_length=30, choices=WidgetTypes.choices)
    attributes = models.ManyToManyField(to=Attribute, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to='events/')
    paper = models.ForeignKey(
        Paper, null=True, blank=True, on_delete=models.CASCADE, related_name='widgets')
    creator = models.ForeignKey('accounts.User', related_name='widgets', null=True, blank=True,
                                on_delete=models.SET_NULL)
    is_hidden = models.BooleanField(default=False)

    @abstractmethod
    def clone(self, paper):
        pass

    def make_file_empty(self):
        try:
            self.file.delete()
        except:
            self.file = None
            self.file.save()
            pass


def clone_widget(widget, paper, *args, **kwargs):
    widget_type = widget.__class__
    model_fields = [
        field.name for field in widget_type._meta.get_fields() if field.name != 'id']
    dicted_model = {name: value for name,
                    value in widget.__dict__.items() if name in model_fields}
    cloned_widget = widget_type(
        **{**dicted_model,
           'paper': paper,
           **kwargs,
           },
    )
    cloned_widget.save()

    cloned_widget_hints = [widget_hint.clone(
        cloned_widget) for widget_hint in widget.hints.all()]

    return cloned_widget


def clone_hint(hint, reference_paper):
    cloned_hint = clone_paper(hint, reference=reference_paper)
    cloned_widgets = [widget.clone(cloned_hint)
                      for widget in hint.widgets.all()]
    return cloned_hint


class WidgetHint(Paper):
    reference = models.ForeignKey(
        Widget, on_delete=models.CASCADE, related_name='hints')

    def clone(self, paper):
        return clone_hint(self, paper)


class TextWidget(Widget):
    text = models.TextField()

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class DetailBoxWidget(Widget):
    title = models.TextField()
    details = models.ForeignKey(Paper, on_delete=models.CASCADE)

    def clone(self, paper):
        cloned_details = self.details  # todo
        return clone_widget(self, paper, details=cloned_details)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Iframe(Widget):
    link = models.URLField()

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Video(Widget):
    link = models.URLField(null=True, blank=True)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Audio(Widget):
    link = models.URLField(null=True, blank=True)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Aparat(Widget):
    video_id = models.TextField()

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Image(Widget):
    link = models.URLField(null=True, blank=True)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


############ PROBLEMS ############


class Problem(Widget):
    text = models.TextField()
    is_required = models.BooleanField(default=False)
    solution = models.TextField(null=True, blank=True)
    be_corrected = models.BooleanField(default=False)
    correctness_threshold = models.IntegerField(default=100)

    @property
    def correct_answer(self):
        return self.answers.filter(is_correct=True).first()

    def unfinalize_older_answers(self, user):
        if isinstance(self.paper, State):
            teammates = Team.objects.get_teammates_from_widget(
                user=user, widget=self)
            older_answers = PROBLEM_ANSWER_MAPPING[self.widget_type].objects.filter(problem=self, is_final_answer=True,
                                                                                    submitted_by__in=teammates)
            for a in older_answers:
                a.is_final_answer = False
                a.save()

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class SmallAnswerProblem(Problem):
    def clone(self, paper):
        return clone_widget(self, paper)


class BigAnswerProblem(Problem):
    def clone(self, paper):
        return clone_widget(self, paper)


class UploadFileProblem(Problem):
    def clone(self, paper):
        return clone_widget(self, paper)


class MultiChoiceProblem(Problem):
    maximum_choices_could_be_chosen = models.IntegerField(
        validators=[MinValueValidator(0)], default=1)

    def clone(self, paper):
        cloned_widget = clone_widget(self, paper)
        cloned_choices = [choice.clone(cloned_widget)
                          for choice in self.choices.all()]
        cloned_widget.save()

    @property
    def correct_answer(self):
        from apps.response.serializers.answers.answer_serializers import MultiChoiceAnswerSerializer
        correct_answer_object = self.answers.filter(is_correct=True).first()
        correct_choices = self.choices.all().filter(is_correct=True)

        if not correct_answer_object:
            correct_answer_serializer = MultiChoiceAnswerSerializer(data={
                'answer_type': 'MultiChoiceAnswer',
                'problem': self,
                'is_correct': True,
            })
            correct_answer_serializer.is_valid(raise_exception=True)
            correct_answer_object = correct_answer_serializer.save()

        correct_answer_object.choices.set(correct_choices)
        correct_answer_object.save()
        return correct_answer_object


class Choice(models.Model):
    problem = models.ForeignKey(MultiChoiceProblem, on_delete=models.CASCADE,
                                related_name='choices')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

    def clone(self, problem):
        cloned_choice = Choice(
            problem=problem,
            text=self.text,
            is_correct=self.is_correct
        )
        cloned_choice.save()
        return cloned_choice

    @classmethod
    def create_instance(self, question: MultiChoiceProblem, choice_data) -> 'Choice':
        return Choice.objects.create(**{
            'problem': question,
            'text': choice_data.get('text'),
            'is_correct': True if choice_data.get('is_correct') else False
        })


############ ANSWERS ############


class Answer(PolymorphicModel):
    class AnswerTypes(models.TextChoices):
        SmallAnswer = 'SmallAnswer'
        BigAnswer = 'BigAnswer'
        MultiChoiceAnswer = 'MultiChoiceAnswer'
        UploadFileAnswer = 'UploadFileAnswer'

    answer_type = models.CharField(max_length=20, choices=AnswerTypes.choices)
    answer_sheet = models.ForeignKey(AnswerSheet, related_name='answers', null=True, blank=True,
                                     on_delete=models.PROTECT)
    submitted_by = models.ForeignKey(
        'accounts.User', related_name='submitted_answers', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_final_answer = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'user: {self.submitted_by.username if self.submitted_by else "-"}'

    @property
    def string_answer(self):
        pass

    @property
    def problem(self):
        return self.problem


class SmallAnswer(Answer):
    problem = models.ForeignKey('fsm.SmallAnswerProblem', null=True,
                                blank=True, on_delete=models.PROTECT, related_name='answers')
    text = models.TextField()

    def correction_status(self):
        if self.problem.correct_answer:
            if self.text.strip() == self.problem.correct_answer.text.strip():
                # TODO - check for semi-correct answers too
                return RegistrationReceipt.CorrectionStatus.Correct
            return RegistrationReceipt.CorrectionStatus.Wrong
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable

    @property
    def string_answer(self):
        return self.text

    def __str__(self):
        return self.text


class BigAnswer(Answer):
    problem = models.ForeignKey('fsm.BigAnswerProblem', null=True, blank=True, on_delete=models.PROTECT,
                                related_name='answers')
    text = models.TextField()

    @property
    def string_answer(self):
        return self.text


class MultiChoiceAnswer(Answer):
    problem = models.ForeignKey(
        MultiChoiceProblem, on_delete=models.PROTECT, related_name='answers')
    choices = models.ManyToManyField(Choice)

    @property
    def string_answer(self):
        return json.dumps([choice.id for choice in self.choices.all()])

    def correction_status(self):
        correct_answer = self.problem.correct_answer
        if correct_answer:
            correct_choices = correct_answer.choices.values_list(['choice'])
            for c in self.choices.values_list(['choice']):
                if c not in correct_choices:
                    return RegistrationReceipt.CorrectionStatus.Wrong
            return RegistrationReceipt.CorrectionStatus.Correct
        return RegistrationReceipt.CorrectionStatus.NoSolutionAvailable


class UploadFileAnswer(Answer):
    problem = models.ForeignKey('fsm.UploadFileProblem', null=True, blank=True, on_delete=models.PROTECT,
                                related_name='answers')
    answer_file = models.URLField(max_length=2000, blank=True)

    @property
    def string_answer(self):
        return self.answer_file


PROBLEM_ANSWER_MAPPING = {
    'SmallAnswerProblem': SmallAnswer,
    'BigAnswerProblem': BigAnswer,
    'MultiChoiceProblem': MultiChoiceAnswer,
    'UploadFileProblem': UploadFileAnswer,
}


############# CERTIFICATE ###########


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
    registration_form = models.ForeignKey(RegistrationForm, on_delete=models.CASCADE,
                                          related_name='certificate_templates')
    font = models.ForeignKey(
        Font, on_delete=models.SET_NULL, related_name='templates', null=True)
    font_size = models.IntegerField(default=100)
