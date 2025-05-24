from django.db import models, transaction
from apps.accounts.models import User
from django.db.models import Q

from apps.fsm.models.base import Object, ObjectMixin, Paper, Widget, clone_paper
from apps.fsm.models.form import AnswerSheet, RegistrationReceipt
from apps.fsm.models.program import Program


class FSMManager(models.Manager):
    @transaction.atomic
    def create(self, **args):
        fsm = super().create(**args)
        if fsm.creator:
            fsm.add_mentor(fsm.creator.id)
        return fsm


class FSM(models.Model, ObjectMixin):
    _object = models.OneToOneField(
        Object, on_delete=models.CASCADE, null=True, related_name='_fsm')

    class FSMLearningType(models.TextChoices):
        Supervised = 'Supervised'
        Unsupervised = 'Unsupervised'

    class FSMPType(models.TextChoices):
        Team = 'Team'
        Individual = 'Individual'
        Hybrid = 'Hybrid'

    class FSMCardType(models.TextChoices):
        vertical1 = 'vertical1'
        horizontal1 = 'horizontal1'

    is_public = models.BooleanField(default=False)

    website = models.CharField(blank=True, null=True, max_length=50)

    program = models.ForeignKey(
        Program, on_delete=models.SET_NULL, related_name='fsms', null=True, blank=True)
    creator = models.ForeignKey('accounts.User', related_name='created_fsms', on_delete=models.SET_NULL, null=True,
                                blank=True)
    mentors = models.JSONField(default=list, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover_image = models.URLField()
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)
    first_state = models.OneToOneField('fsm.State', null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name='my_fsm')
    fsm_learning_type = models.CharField(max_length=40, default=FSMLearningType.Unsupervised,
                                         choices=FSMLearningType.choices)
    fsm_p_type = models.CharField(
        max_length=40, default=FSMPType.Individual, choices=FSMPType.choices)
    team_size = models.IntegerField(default=3)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    card_type = models.CharField(
        max_length=20, default=FSMCardType.vertical1, choices=FSMCardType.choices)
    show_roadmap = models.BooleanField(default=True)
    show_player_performance_on_end = models.BooleanField(
        default=False,
        help_text='If enabled, the player\'s performance analysis will be shown to them after completing the FSM.'
    )
    participant_limit = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(
        default=0,
        help_text='Duration in minutes. 0 means unlimited.'
    )

    objects = FSMManager()

    def __str__(self):
        return self.name

    # default is False
    def is_enabled(self, user) -> bool:
        # check ceil of participation
        finished_players = Player.objects.filter(
            user=user,
            fsm=self,
            finished_at__isnull=False,
        )
        if finished_players.count() >= self.participant_limit:
            return False

        return super().is_enabled(user=user)

    @transaction.atomic
    def clone(self):
        # 0) clone the underlying Object so you carry over title, attributes, position, etc.
        new_obj = self._object.clone()

        # 1) pick up every scalar field you want to duplicate
        clone_fields = [
            'name', 'description', 'cover_image', 'is_active', 'is_public', 'website',
            'is_visible', 'fsm_learning_type', 'fsm_p_type', 'team_size',
            'show_roadmap', 'show_player_performance_on_end',
            'participant_limit', 'duration', 'card_type', 'program_id',
        ]
        data = {f: getattr(self, f) for f in clone_fields}

        # inject the cloned Object
        data.update({
            '_object': new_obj,
        })

        # 2) create the new FSM
        cloned_fsm = FSM.objects.create(**data)

        # 3) clone all states (which now also clones their papers, via State.clone)
        state_map = {
            state.pk: state.clone(fsm=cloned_fsm)
            for state in self.states.all()
        }

        # 4) re‐wire edges between cloned states
        for orig in self.states.all():
            for edge in orig.outward_edges.all():
                edge.clone(
                    tail=state_map[orig.pk],
                    head=state_map[edge.head_id]
                )

        # 5) point at the new first_state
        if self.first_state_id in state_map:
            cloned_fsm.first_state = state_map[self.first_state_id]
            cloned_fsm.save(update_fields=['first_state'])

        return cloned_fsm

    def get_fsm(fsm_id: int):
        return FSM.objects.filter(id=fsm_id).first()

    def get_questions(self):
        states = self.states.all()
        questions = []
        for state in states:
            papers = state.papers.all()
            for paper in papers:
                questions += paper.widgets.filter(
                    widget_type__in=[
                        Widget.WidgetTypes.SmallAnswerProblem,
                        Widget.WidgetTypes.BigAnswerProblem,
                        Widget.WidgetTypes.MultiChoiceProblem,
                        Widget.WidgetTypes.UploadFileProblem
                    ]
                )
        return questions

    def get_mentor_role(self, user_id: str) -> str:
        """
        Returns the role of the given user_id from mentors.
        If user is not a mentor, returns None.
        """
        user_id_str = str(user_id)

        for mentor in self.mentors:
            if mentor.get("id") == user_id_str:
                return mentor.get("role")

        return None

    def add_mentor(self, user_id: str, role: str = "manager") -> bool:
        """
        Adds a mentor to mentors if not already present.
        Returns True if added, False if already exists.
        """
        user_id_str = str(user_id)

        if not self.mentors:
            self.mentors = []

        for mentor in self.mentors:
            if mentor.get("id") == user_id_str:
                return False  # Already exists

        self.mentors.append({"id": user_id_str, "role": role})
        self.save(update_fields=["mentors"])
        return True

    def remove_mentor(self, user_id: str) -> bool:
        """
        Removes a mentor from mentors by user_id.
        Returns True if removed, False if not found.
        """
        if not self.mentors:
            return False

        user_id_str = str(user_id)

        new_list = [m for m in self.mentors if m.get("id") != user_id_str]
        if len(new_list) == len(self.mentors):
            return False  # Not found

        self.mentors = new_list
        self.save(update_fields=["mentors"])
        return True

    def update_mentor_role(self, user_id: str, new_role: str) -> bool:
        """
        Updates role of an existing mentor.
        Returns True if updated, False if user not found.
        """
        if not self.mentors:
            return False

        user_id_str = str(user_id)

        updated = False
        for mentor in self.mentors:
            if mentor.get("id") == user_id_str:
                mentor["role"] = new_role
                updated = True
                break

        if updated:
            self.save(update_fields=["mentors"])
        return updated


class Player(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        to=User,
        related_name='players',
        on_delete=models.CASCADE,
    )
    fsm = models.ForeignKey(
        to=FSM,
        related_name='players',
        on_delete=models.CASCADE,
    )

    @property
    def answer_sheet(self):
        if not self._answer_sheet:
            new_sheet = AnswerSheet.objects.create(user=self.user)
            self._answer_sheet = new_sheet
            self.save()
        return self._answer_sheet

    _answer_sheet = models.ForeignKey(
        to=AnswerSheet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    current_state = models.ForeignKey(
        to='fsm.State',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='players',
    )

    last_visit = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # todo: think about it. should player really connect to receipt?
    receipt = models.ForeignKey(
        RegistrationReceipt,
        related_name='players',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @staticmethod
    def get_player(player_id: int):
        return Player.objects.filter(id=player_id).first()

    def __str__(self):
        return f'{self.user.full_name} in {self.fsm.name}'

    def get_previous_state(self):
        from apps.fsm.utils.utils import get_last_forward_transition
        last_forward_transition = get_last_forward_transition(self)
        return last_forward_transition.source_state

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'fsm'],
                condition=Q(finished_at__isnull=True),
                name='unique_active_player'
            )
        ]
        indexes = [
            # get_players: fsm.players.filter(user=user)
            models.Index(fields=['fsm', 'user'], name='idx_player_fsm_user'),
            # lookup or get_or_create by (user, fsm, finished_at__isnull=True)
            models.Index(fields=['user', 'fsm', 'finished_at'],
                         name='idx_player_user_fsm_finished'),
            # filtering lists of players by fsm (e.g. players_count, PlayerViewSet.players)
            models.Index(fields=['fsm'], name='idx_player_fsm'),
            # filtering a user’s history (e.g. get_current_user_player → filter(user=…))
            models.Index(fields=['user'], name='idx_player_user'),
            # fast jump to a player’s current state in go_backward()
            models.Index(fields=['current_state'],
                         name='idx_player_current_state'),
        ]


class StatePaper(models.Model):
    state = models.ForeignKey('fsm.State', on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('paper', 'state')
        indexes = [
            # update_paper_order/remove_paper:  queries by (state, paper)
            models.Index(fields=['state', 'paper'],
                         name='idx_statepaper_state_paper'),
            # StateSerializer.get_papers():  filter+order by state & order
            models.Index(fields=['state', 'order'],
                         name='idx_statepaper_state_order'),
        ]


class State(Object):
    class PaperTemplate(models.TextChoices):
        normal = 'normal'
        board = 'board'

    papers = models.ManyToManyField(
        to=Paper,
        default=list,
        through=StatePaper,
        related_name='states',
    )
    template = models.CharField(
        max_length=20, default=PaperTemplate.normal, choices=PaperTemplate.choices)
    fsm = models.ForeignKey(
        FSM, on_delete=models.CASCADE, related_name='states')
    show_appbar = models.BooleanField(default=True)
    is_end = models.BooleanField(default=False)

    @transaction.atomic
    def delete(self):
        try:
            if self.my_fsm:
                fsm = self.fsm
                fsm.first_state = fsm.states.exclude(id=self.id).first()
                fsm.save()
        except:
            pass
        return super().delete()

    @transaction.atomic
    def clone(self, fsm):
        # 1) pick up all scalar fields from both Object (base) and State (subclass)
        clone_fields = [
            # from Object (PolymorphicModel):
            'title', 'name', 'creator', 'is_private', 'order', 'is_hidden', 'website',
            # from State:
            'template', 'show_appbar', 'is_end',
        ]

        # build the kwargs for the new instance
        data = {f: getattr(self, f) for f in clone_fields}
        data['fsm'] = fsm

        # 2) create the new State row
        cloned_state = State.objects.create(**data)

        # 3) copy over any attributes (the M2M on Object)
        cloned_state.attributes.set(self.attributes.all())

        # 4) deep‑clone every Paper via the through‑model (preserving order)
        for paper in self.papers.all():
            state_paper = StatePaper.objects.get(state=self, paper=paper)
            new_paper = paper.clone()   # your Paper.clone() should recurse into widgets/hints
            StatePaper.objects.create(
                state=cloned_state,
                paper=new_paper,
                order=state_paper.order
            )

        # 5) clone any loose hints attached directly to this State
        for hint in self.hints.all():
            hint.clone(cloned_state)

        return cloned_state

    def __str__(self):
        return f'گام: {self.title} | کارگاه: {self.fsm}'

    class Meta:
        indexes = [
            models.Index(fields=['fsm'], name='state_fsm_idx'),
        ]


class Edge(models.Model, ObjectMixin):
    _object = models.OneToOneField(
        Object, on_delete=models.CASCADE, null=True, related_name='edge')

    tail = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='outward_edges')
    head = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='inward_edges')
    is_back_enabled = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=False)

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
        return f'از {self.tail.title} به {self.head.title}'

    class Meta:
        unique_together = ('tail', 'head')
        indexes = [
            # used by EdgeViewSet.create() & other filters:
            #   Edge.objects.filter(tail=…, head=…)
            models.Index(fields=['tail', 'head'], name='idx_edge_tail_head'),
            # used by StateViewSet.inward_edges()/outward_edges():
            #   Edge.objects.filter(head=…)  and  filter(tail=…)
            models.Index(fields=['head'], name='idx_edge_head'),
            models.Index(fields=['tail'], name='idx_edge_tail'),
        ]


class PlayerTransition(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, related_name='player_transitions')
    source_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, related_name='player_departure_transitions')
    target_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, null=True, related_name='player_arrival_transitions')
    time = models.DateTimeField()
    transited_edge = models.ForeignKey(
        Edge, related_name='player_transitions', null=True, on_delete=models.SET_NULL)
    is_backward = models.BooleanField(default=False)
    reverted_by = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reverts'
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.is_backward:
            try:
                _ = self.reverts
                return
            except PlayerTransition.DoesNotExist:
                pass

            try:
                forward = PlayerTransition.objects.filter(
                    player=self.player,
                    source_state=self.target_state,
                    target_state=self.source_state,
                    is_backward=False,
                    reverted_by__isnull=True
                ).latest('time')
            except PlayerTransition.DoesNotExist:
                forward = None

            if forward:
                forward.reverted_by = self
                forward.save()

    class Meta:
        indexes = [
            # Speeds up `player.player_transitions.order_by('time')`
            models.Index(fields=['player', 'time']),
            # Speeds up get_last_forward_transition filters + order_by('-time')
            models.Index(
                fields=[
                    'player',
                    'target_state',
                    'is_backward',
                    'reverted_by',
                    'time',
                ],
                name='pt_tgt_bw_rev_time_ix'
            ),
        ]

    def __str__(self):
        direction = 'backward' if self.is_backward else 'forward'
        return f"{self.player} | {self.source_state} → {self.target_state} ({direction})"


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
        return f'{self.player} - {self.state.title if self.state else "DELETED"}'

    class Meta:
        indexes = [
            # transit_player_in_fsm:
            #   player.player_state_histories.filter(state=…, departure=None)
            models.Index(
                fields=['player', 'state', 'departure'],
                name='idx_psh_player_state_dep'
            ),
        ]
