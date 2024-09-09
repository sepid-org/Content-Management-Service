import uuid
from django.db import models


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
