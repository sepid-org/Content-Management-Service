from datetime import timezone, datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from apps.fsm.models import RegistrationReceipt, Program, RegistrationForm, FSM, Problem, State, Team


class ProgramAdminPermission(permissions.BasePermission):
    """
    Permission for program's admin to manage program
    """
    message = 'You are not this program\'s admin'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.modifiers


def is_form_modifier(form, user):
    return (form.program_or_fsm and user in form.program_or_fsm.modifiers) or user == form.creator


class IsRegistrationFormModifier(permissions.BasePermission):
    """
    Permission for form's admin to update form
    """
    message = 'You are not this registration_form\'s modifier'

    def has_object_permission(self, request, view, obj):
        return is_form_modifier(obj, request.user)


class IsCertificateTemplateModifier(permissions.BasePermission):
    """
    Permission for certificate template modifiers
    """

    message = 'You are not this certificate template\'s registration_form modifier'

    def has_object_permission(self, request, view, obj):
        form = obj.registration_form
        return form and is_form_modifier(form, request.user)


class IsRegistrationReceiptOwner(permissions.BasePermission):
    """
    Permission for registration receipt owner to get
    """
    message = 'You are not the owner of this form'

    def has_object_permission(self, request, view, obj):
        result = False
        result |= obj.user == request.user
        if obj.form.program:
            result |= ProgramAdminPermission().has_object_permission(request, view, obj.form.program)
        return result


class IsReceiptsFormModifier(permissions.BasePermission):
    """
    Permission for receipt's registration form modifiers
    """
    message = 'You are not this registration receipt\'s registration form modifier'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.form.program_or_fsm.modifiers


class IsArticleModifier(permissions.BasePermission):
    """
    Permission for editing an article
    """
    message = 'You are not this article\'s modifier'

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class IsTeamModifier(permissions.BasePermission):
    """
    Permission for team's modifier
    """
    message = 'You are not this team\'s modifier (program owner/team head)'

    def has_object_permission(self, request, view, obj):
        head = obj.team_head
        if head and obj.team_head.user == request.user:
            return True
        fsm_modifiers = obj.program.modifiers
        if request.user in fsm_modifiers:
            return True
        return False


class IsTeamHead(permissions.BasePermission):
    """
    Permission for team's head
    """
    message = 'You are not this team\'s head'

    def has_object_permission(self, request, view, obj):
        return obj.team_head.user == request.user


class IsInvitationInvitee(permissions.BasePermission):
    """
    Permission for invitation's invitee
    """
    message = 'you are not this invitation\'s invitee'

    def has_object_permission(self, request, view, obj):
        return obj.invitee.user == request.user


class IsTeamMember(permissions.BasePermission):
    """
    Permission for team's members
    """
    message = 'you are not a member of this team'

    def has_object_permission(self, request, view, obj):
        return len(obj.members.filter(user=request.user)) == 1


class FSMMentorPermission(permissions.BasePermission):
    """
    Permission for mentor
    """
    message = 'you are not a mentor of this fsm'

    def has_object_permission(self, request, view, obj):
        return obj.get_mentor_role(request.user.id) is not None or ProgramAdminPermission().has_object_permission(request, view, obj.program)


class MentorCorrectionPermission(permissions.BasePermission):
    """
    Permission for mentor correcting answers
    """
    message = 'you can\'t correct this answer'

    def has_object_permission(self, request, view, obj):
        if isinstance(obj.problem.paper, State):
            return obj.problem.paper.fsm.get_mentor_role(request.user.id) is not None
        elif isinstance(obj.problem.paper, RegistrationForm):
            return is_form_modifier(obj.problem.paper, request.user)
        else:
            return request.user.is_staff or request.user.is_superuser


class PlayerViewerPermission(permissions.BasePermission):
    """
    Permission for viewing player
    """
    message = 'you don\'t have necessary access to view this player'

    def has_object_permission(self, request, view, obj):
        return obj.fsm.get_mentor_role(request.user.id) is not None


class IsStateModifier(permissions.BasePermission):
    """
    Permission for mentors modifying states
    """
    message = 'you are not this state\'s modifier'

    def has_object_permission(self, request, view, obj):
        return obj.fsm.get_mentor_role(request.user.id) is not None


class IsHintModifier(permissions.BasePermission):
    """
    Permission for mentors modifying hints
    """
    message = 'you are not this hint\'s modifier'

    def has_object_permission(self, request, view, obj):
        return obj.reference.fsm.get_mentor_role(request.user.id) is not None


class IsEdgeModifier(permissions.BasePermission):
    """
    Permission for mentors modifying edges
    """
    message = 'you are not this edge\'s modifier'

    def has_object_permission(self, request, view, obj):
        return obj.tail.fsm.get_mentor_role(request.user.id) is not None or \
            obj.head.fsm.get_mentor_role(request.user.id) is not None


class IsAnswerModifier(permissions.BasePermission):
    """
    Permission for modifying answers
    """
    message = 'you are not this answer\'s modifier'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.submitted_by


class HasActiveRegistration(permissions.BasePermission):
    """
    Permission for checking registration of users in programs / fsms
    """
    message = 'you don\'t have an active registration receipt for this entity'

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Program):
            return len(RegistrationReceipt.objects.filter(user=request.user, form=obj.registration_form,
                                                          is_participating=True)) > 0
        elif isinstance(obj, FSM):
            if obj.program:
                return len(
                    RegistrationReceipt.objects.filter(user=request.user, form=obj.program.registration_form,
                                                       is_participating=True)) > 0
            else:
                return len(
                    RegistrationReceipt.objects.filter(user=request.user, form=obj.registration_form,
                                                       is_participating=True))


class ParticipantPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user
        try:
            if user.is_participant:
                return True
        except:
            return False
        return False


class ActiveTeamsPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # user = request.user
        # try:
        #     if user.participant.team.is_team_active():
        #         return True
        # except:
        #     return False
        # return False
        return True


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.creator == request.user
