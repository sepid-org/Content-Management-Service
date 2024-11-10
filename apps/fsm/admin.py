import csv
from datetime import timedelta
from django.utils import timezone

from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
from import_export.admin import ExportActionMixin

from apps.fsm.models import Choice, DetailBoxWidget, Edge, Paper, PlayerTransition, ProgramContactInfo, RegistrationForm, Problem, AnswerSheet, RegistrationReceipt, Team, \
    Invitation, CertificateTemplate, Font, FSM, WidgetHint, Hint, Widget, Video, Audio, Image, Player, Iframe, SmallAnswerProblem, \
    SmallAnswer, BigAnswerProblem, BigAnswer, MultiChoiceProblem, MultiChoiceAnswer, Answer, TextWidget, Program, \
    UploadFileAnswer, UploadFileProblem, PlayerStateHistory, Article, Tag, Aparat, Position, Object

from apps.fsm.models.base import GeneralHint
from apps.fsm.models.content_widgets import Placeholder
from apps.fsm.models.fsm import State, StatePaper


@admin.register(ProgramContactInfo)
class ProgramContactInfoCustomAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = []


class EdgeAdmin(admin.ModelAdmin):
    model = Edge
    list_display = ['id', 'head_title', 'tail_title', 'is_visible']
    list_filter = ['is_visible', 'head__title', 'tail__title']

    def head_title(self, obj):
        name = obj.head.title
        return name

    def tail_title(self, obj):
        name = obj.tail.title
        return name

    head_title.short_description = "به "
    tail_title.short_description = "از "


class UploadFileAnswerAdmin(admin.ModelAdmin):
    model = UploadFileAnswer
    list_display = ['id', 'problem', 'answer_file', 'is_final_answer']
    list_filter = ['problem', 'is_final_answer']


class PlayerHistoryAdmin(ExportActionMixin, admin.ModelAdmin):
    model = PlayerStateHistory
    list_display = ['player', 'state', 'delta_time']
    list_filter = ['arrival__time', 'departure__time', 'state__fsm']
    raw_id_fields = ('player', 'state', 'arrival', 'departure')

    def delta_time(self, obj):
        if (obj.departure and obj.arrival):
            return obj.departure.time - obj.arrival.time
        return "-"


@admin.register(PlayerTransition)
class PlayerTransitionAdmin(admin.ModelAdmin):
    model = PlayerTransition
    readonly_fields = ('time',)
    list_display = ['player', 'source_state',
                    'target_state', 'time', 'transited_edge']
    list_filter = []
    raw_id_fields = ('player', 'source_state',
                     'target_state', 'transited_edge')


class TextWidgetAdmin(admin.ModelAdmin):
    model = TextWidget
    list_display = ['paper', 'text']

    def paper(self, obj):
        return obj.paper.id

    def text(self, obj):
        name = str(obj.text)[0:100]
        return name


class DetailBoxWidgetAdmin(admin.ModelAdmin):
    model = DetailBoxWidget
    list_display = ['id', 'title', 'details']


class PaperAdmin(admin.ModelAdmin):
    model = Paper
    list_display = ['id']
    list_filter = []
    search_fields = ['id']


class RegistrationFormAdmin(admin.ModelAdmin):

    def get_registration_status_for_users(self, request, queryset):
        if len(queryset) > 0:
            selected = queryset.values_list('pk', flat=True)[0]
            # TODO: fix bug
            return HttpResponseRedirect(f'/api/admin/export_registration_data/?q={selected}')

    def participants_count(self, obj):
        return len(obj.registration_receipts.all())

    model = RegistrationForm
    list_display = ['id', 'program_or_fsm', 'accepting_status',
                    'min_grade', 'max_grade', 'audience_type', 'participants_count']
    list_display_links = ['id', 'program_or_fsm']
    actions = [get_registration_status_for_users]


def delete_registration_receipts(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


class RegistrationReceiptsAdmin(admin.ModelAdmin):
    list_display = ['user', 'form', 'status', 'is_participating', 'team']
    list_filter = ['form', 'status', 'is_participating']
    actions = [delete_registration_receipts]


class PlayerAdmin(admin.ModelAdmin):
    model = Player
    list_display = ['id', 'user', 'fsm', 'current_state', 'last_visit']
    list_filter = ['last_visit', 'fsm', 'current_state']
    search_fields = ['user__username']


def clone_fsm(modeladmin, request, queryset):
    for fsm in queryset:
        fsm.clone()


class FSMAdmin(admin.ModelAdmin):
    model = FSM
    list_display = ['name', 'first_state', 'is_active',
                    'mentors_num', 'mentors_list', 'online_teams_in_last_hour']
    list_filter = ['name']
    search_fields = ['name']
    autocomplete_fields = ['creator', 'mentors',
                           'program', 'first_state', '_object']
    actions = [clone_fsm]

    def mentors_list(self, obj):
        return ','.join(m.full_name for m in obj.mentors.all())

    def mentors_num(self, obj):
        return len(obj.mentors.all())

    def online_teams_in_last_hour(self, obj):
        return round(len(obj.players.filter(
            last_visit__gt=timezone.now() - timedelta(hours=1))) / obj.team_size if obj.team_size > 0 else 1)


def download_team_info_csv(modeladmin, request, queryset):
    import csv
    f = open('teams-info.csv', 'w', encoding="utf-8")
    writer = csv.writer(f)
    writer.writerow(['team_name', 'users'])
    for team in queryset:
        members = team.members.all()
        team_info = [team.name, ]
        for member in members:
            team_info.append(
                f'{member.user.first_name} {member.user.last_name}')
        writer.writerow(team_info)

    f.close()
    f = open('teams-info.csv', 'r')
    response = HttpResponse(f, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=teams-info.csv'
    return response


class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ['name', 'program', 'team_head',
                    'members', 'has_been_online_in_last_hour']
    list_filter = ['program']
    search_fields = ['name']
    actions = [download_team_info_csv]

    def members(self, obj):
        return ', '.join(member.user.full_name for member in obj.members.all())

    def has_been_online_in_last_hour(self, obj):
        for m in obj.members.all():
            if m.players.filter(last_visit__gt=timezone.now() - timedelta(hours=1)).first():
                return True
        return False


class SmallAnswerProblemAdmin(admin.ModelAdmin):
    list_display = ['paper', 'widget_type', 'creator']
    list_filter = ['widget_type']
    search_fields = []


class BigAnswerProblemAdmin(admin.ModelAdmin):
    list_display = ['paper', 'widget_type', 'creator']
    list_filter = ['widget_type']
    search_fields = []


@admin.register(AnswerSheet)
class AnswerSheetCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer_sheet_type']
    list_display_links = ['id', 'answer_sheet_type']
    list_filter = ['answer_sheet_type']
    search_fields = ['answer_sheet_type']


@admin.register(MultiChoiceAnswer)
class MultiChoiceAnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem']
    list_display_links = ['id', 'problem']
    list_filter = ['problem']


@admin.register(Invitation)
class InvitationCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'invitee', 'team', 'status']
    list_display_links = ['id', 'invitee', 'team']
    list_filter = ['status']


@admin.register(CertificateTemplate)
class CertificateTemplateCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'certificate_type', 'registration_form', 'font_size']
    list_display_links = ['id', 'certificate_type']
    list_filter = ['certificate_type']
    search_fields = ['certificate_type']


@admin.register(Answer)
class AnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer_type', 'answer_sheet',
                    'submitted_by', 'is_final_answer', 'is_correct', 'created_at']
    list_filter = ['answer_type', 'is_final_answer',
                   'is_correct', 'created_at']
    search_fields = ['submitted_by__username']


@admin.register(BigAnswer)
class BigAnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_final_answer']
    list_filter = ['problem', 'is_final_answer']

    def name(self, obj):
        return obj.problem.name

    def widget_type(self, obj):
        return obj.problem.widget_type

    def creator(self, obj):
        return obj.problem.creator


@admin.register(SmallAnswer)
class SmallAnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'widget_type', 'creator']
    list_filter = []

    def name(self, obj):
        return obj.problem.name

    def widget_type(self, obj):
        return obj.problem.widget_type

    def creator(self, obj):
        return obj.problem.creator


@admin.register(Article)
class ArticleCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'publisher',
                    'all_tags', 'is_draft']
    list_filter = ['is_draft', 'publisher']

    def all_tags(self, obj):
        return ','.join(m.name for m in obj.tags.all())


@admin.register(Iframe)
class IframeCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'creator', 'link']
    list_filter = []
    search_fields = ['link']


@admin.register(Video)
class VideoCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_filter = []
    search_fields = []
    actions = []


@admin.register(Audio)
class AudioCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_filter = []
    search_fields = []


@admin.register(Aparat)
class AparatCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_filter = []
    search_fields = []


@admin.register(Image)
class ImageCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_filter = []
    search_fields = []
    actions = []


@admin.register(Hint)
class HintCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper_type', 'creator']
    list_filter = ['paper_type']


@admin.register(WidgetHint)
class WidgetHintCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper_type', 'creator']
    list_filter = ['paper_type']


@admin.register(Program)
class ProgramCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'registration_form', 'creator']
    list_display_links = ['id', 'name']
    search_fields = ['name']


@admin.register(UploadFileProblem)
class UploadFileProblemCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_display_links = ['id']
    list_filter = ['widget_type']
    search_fields = []


admin.site.register(Paper, PaperAdmin)
admin.site.register(RegistrationForm, RegistrationFormAdmin)
admin.site.register(RegistrationReceipt, RegistrationReceiptsAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Font)
admin.site.register(FSM, FSMAdmin)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(BigAnswerProblem, BigAnswerProblemAdmin)
admin.site.register(SmallAnswerProblem, SmallAnswerProblemAdmin)
admin.site.register(TextWidget, TextWidgetAdmin)
admin.site.register(DetailBoxWidget, DetailBoxWidgetAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerStateHistory, PlayerHistoryAdmin)
admin.site.register(UploadFileAnswer, UploadFileAnswerAdmin)
admin.site.register(Tag)


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'creator']
    list_filter = ['widget_type']
    autocomplete_fields = ['paper', 'creator', '_object']
    search_fields = ['_object__title']


@admin.register(Problem)
class ProblemCustomAdmin(WidgetAdmin):
    list_display = WidgetAdmin.list_display + ['is_required']
    list_filter = WidgetAdmin.list_filter + ['is_required']


class ChoiceInline(admin.TabularInline):
    model = Choice


@admin.register(MultiChoiceProblem)
class MultiChoiceProblemCustomAdmin(ProblemCustomAdmin):
    list_display = ProblemCustomAdmin.list_display + []
    inlines = [ChoiceInline]


@admin.register(StatePaper)
class StatePaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper']


class StatePaperInline(admin.TabularInline):
    model = StatePaper
    extra = 1


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    model = State
    inlines = [StatePaperInline]
    list_display = ['id', 'title', 'fsm']
    list_filter = ['fsm']
    search_fields = ['title']


@admin.register(Position)
class RegistrationFormCAdmin(admin.ModelAdmin):
    list_display = ('object', 'x', 'y', 'width', 'height')
    search_fields = ('object__title',)


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('id', 'title',)
    filter_horizontal = ['attributes',]


@admin.register(GeneralHint)
class GeneralHintCustomAdmin(ObjectAdmin):
    list_display = ['id', 'title', 'target_object', 'hint_content']
    autocomplete_fields = ['target_object', 'hint_content']


@admin.register(Placeholder)
class PlaceholderAdmin(admin.ModelAdmin):
    model = Placeholder
    list_display = ['id', 'name', 'title']
