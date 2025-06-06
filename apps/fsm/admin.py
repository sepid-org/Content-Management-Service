import csv
from datetime import timedelta
from django.utils import timezone

from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
from import_export.admin import ExportActionMixin

from apps.fsm.models import Choice, DetailBoxWidget, Edge, Paper, PlayerTransition, ProgramContactInfo, RegistrationForm, Problem, AnswerSheet, RegistrationReceipt, Team, \
    Invitation, CertificateTemplate, Font, FSM, WidgetHint, Hint, Widget, Video, Audio, Image, Player, Iframe, SmallAnswerProblem, \
    SmallAnswer, BigAnswerProblem, BigAnswer, MultiChoiceProblem, MultiChoiceAnswer, Answer, TextWidget, Program, \
    UploadFileAnswer, UploadFileProblem, Article, Tag, Aparat, Position, Object

from apps.fsm.models.base import GeneralHint, Resource
from apps.fsm.models.content_widgets import Placeholder
from apps.fsm.models.form import Form
from apps.fsm.models.fsm import State, StatePaper


@admin.register(ProgramContactInfo)
class ProgramContactInfoCustomAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = []
    search_fields = ['id']


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


@admin.register(PlayerTransition)
class PlayerTransitionAdmin(admin.ModelAdmin):
    model = PlayerTransition
    readonly_fields = ('time',)
    list_display = ['player', 'source_state', 'target_state', 'time']
    search_fields = ['player__id']
    raw_id_fields = ('player', 'source_state', 'target_state', 'reverted_by')


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


################### PAPER ###################


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = []
    search_fields = ['id']
    autocomplete_fields = ['creator', '_object']


@admin.register(Article)
class ArticleCustomAdmin(PaperAdmin):
    list_display = ['id', 'name', 'all_tags']
    list_filter = ['website']
    autocomplete_fields = PaperAdmin.autocomplete_fields + []

    def all_tags(self, obj):
        return ','.join(m.name for m in obj.tags.all())

######################################


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
    search_fields = ['id', '_object__title']
    autocomplete_fields = ['_object', 'creator']


@admin.register(Form)
class FormAdmin(PaperAdmin):
    list_display = PaperAdmin.list_display + \
        ['audience_type', 'start_date', 'end_date']
    list_filter = PaperAdmin.list_filter + []
    search_fields = PaperAdmin.search_fields + ['id']
    autocomplete_fields = PaperAdmin.autocomplete_fields + []


def delete_registration_receipts(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


class PlayerAdmin(admin.ModelAdmin):
    model = Player
    list_display = ['id', 'user', 'fsm', 'current_state', 'last_visit']
    list_filter = ['last_visit', 'fsm']
    autocomplete_fields = ['user', 'fsm',
                           '_answer_sheet', 'current_state', 'receipt']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']


def clone_fsm(modeladmin, request, queryset):
    for fsm in queryset:
        fsm.clone()


class FSMAdmin(admin.ModelAdmin):
    model = FSM
    list_display = ['name', 'first_state',
                    'is_active', 'online_teams_in_last_hour']
    list_filter = ['name']
    search_fields = ['name']
    autocomplete_fields = ['creator',
                           'program', 'first_state', '_object']
    actions = [clone_fsm]

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
    list_display = ['id', 'answer_sheet_type', 'user', 'form']
    autocomplete_fields = ['user', 'form']
    list_filter = ['form']
    search_fields = ['answer_sheet_type']


@admin.register(RegistrationReceipt)
class RegistrationReceiptsAdmin(AnswerSheetCustomAdmin):
    list_display = ['user', 'form', 'status', 'is_participating', 'team']
    list_filter = ['form', 'status', 'is_participating']
    actions = [delete_registration_receipts]
    search_fields = ['user__username']
    autocomplete_fields = AnswerSheetCustomAdmin.autocomplete_fields + ['team']


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


################### ANSWERS ###################

@admin.register(Answer)
class AnswerCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer_type', 'answer_sheet',
                    'submitted_by', 'is_final_answer', 'is_correct', 'created_at']
    autocomplete_fields = ['answer_sheet', 'submitted_by']
    list_filter = ['answer_type', 'is_final_answer',
                   'is_correct', 'created_at']
    search_fields = ['submitted_by__username',
                     'submitted_by__first_name', 'submitted_by__last_name']


@admin.register(BigAnswer)
class BigAnswerCustomAdmin(AnswerCustomAdmin):
    list_display = ['id', 'is_final_answer']
    list_filter = ['problem', 'is_final_answer']

    def name(self, obj):
        return obj.problem.name

    def widget_type(self, obj):
        return obj.problem.widget_type

    def creator(self, obj):
        return obj.problem.creator


@admin.register(SmallAnswer)
class SmallAnswerCustomAdmin(AnswerCustomAdmin):
    list_display = ['id', 'widget_type', 'creator']
    list_filter = []

    def name(self, obj):
        return obj.problem.name

    def widget_type(self, obj):
        return obj.problem.widget_type

    def creator(self, obj):
        return obj.problem.creator


@admin.register(MultiChoiceAnswer)
class MultiChoiceAnswerCustomAdmin(AnswerCustomAdmin):
    list_display = ['id', 'problem']
    list_display_links = ['id', 'problem']
    list_filter = ['problem']


@admin.register(UploadFileAnswer)
class UploadFileAnswerAdmin(AnswerCustomAdmin):
    model = UploadFileAnswer
    list_display = ['id', 'problem', 'answer_file', 'is_final_answer']
    list_filter = ['problem', 'is_final_answer']


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
    autocomplete_fields = ['admins',  'registration_form',
                           'program_contact_info', 'creator', 'menu']


@admin.register(UploadFileProblem)
class UploadFileProblemCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_display_links = ['id']
    list_filter = ['widget_type']
    search_fields = []


admin.site.register(RegistrationForm, RegistrationFormAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Font)
admin.site.register(FSM, FSMAdmin)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(BigAnswerProblem, BigAnswerProblemAdmin)
admin.site.register(SmallAnswerProblem, SmallAnswerProblemAdmin)
admin.site.register(TextWidget, TextWidgetAdmin)
admin.site.register(DetailBoxWidget, DetailBoxWidgetAdmin)
admin.site.register(Player, PlayerAdmin)
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
    autocomplete_fields = ['state', 'paper']


class StatePaperInline(admin.TabularInline):
    model = StatePaper
    autocomplete_fields = ['state', 'paper']
    extra = 1


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    model = State
    inlines = [StatePaperInline]
    list_display = ['id', 'title', 'fsm']
    list_filter = ['fsm']
    autocomplete_fields = ['fsm']
    search_fields = ['title']


@admin.register(Position)
class PositionCustomAdmin(admin.ModelAdmin):
    list_display = ('object', 'x', 'y', 'width', 'height')
    search_fields = ('object__title',)
    autocomplete_fields = ['object']


class PositionInline(admin.StackedInline):
    model = Position
    can_delete = False
    # Because Position.object is a OneToOneField, Django will create exactly one inline form when it exists.
    fk_name = 'object'
    verbose_name = 'Position'
    verbose_name_plural = 'Position'


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('id', 'title',)
    filter_horizontal = ['attributes',]
    inlines = (PositionInline,)

    def position_summary(self, obj):
        """
        Show a brief summary of the related Position in the changelist.
        If no Position exists, return a dash or “None.”
        """
        try:
            pos = obj.position
            # Customize this string any way you like; here we show x,y and WxH.
            return f"({pos.x}, {pos.y}) – {pos.width}×{pos.height}"
        except Position.DoesNotExist:
            return "—"
    position_summary.short_description = "Position"


@admin.register(GeneralHint)
class GeneralHintCustomAdmin(ObjectAdmin):
    list_display = ['id', 'title', 'target_object', 'hint_content']
    autocomplete_fields = ['target_object', 'hint_content']


@admin.register(Resource)
class ResourceCustomAdmin(ObjectAdmin):
    list_display = ['id', 'title', 'type', 'target_object', 'content']
    list_filter = ['type']
    autocomplete_fields = ['target_object']


@admin.register(Placeholder)
class PlaceholderAdmin(admin.ModelAdmin):
    model = Placeholder
    list_display = ['id', 'name', 'title']
