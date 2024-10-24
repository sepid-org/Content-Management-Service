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

from apps.fsm.models.content_widgets import Placeholder
from apps.fsm.models.fsm import State, StatePaper
from apps.fsm.utils import get_django_file


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


class WidgetAdmin(admin.ModelAdmin):
    model = Widget
    list_display = ['id', 'widget_type', 'paper']
    list_filter = ['widget_type']
    search_fields = []


class PaperAdmin(admin.ModelAdmin):
    model = Paper
    list_display = ['id']
    list_filter = []


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


def download_csv(modeladmin, request, queryset):
    import csv
    f = open('registration_receipts.csv', 'w')
    writer = csv.writer(f)
    a_receipt = queryset[0]
    problems = []
    for widget in a_receipt.form.widgets.all():
        print(widget.widget_type)
        if 'problem' in widget.widget_type.lower():
            problem = widget
            problems.append(problem.id)
    header = ['user', 'status', 'is_participating', 'team']
    writer.writerow(
        header + [f'widget {problem}' for problem in problems])
    for registration_receipt in queryset:
        row = [registration_receipt.user, registration_receipt.status,
               registration_receipt.is_participating, registration_receipt.team]
        answers = registration_receipt.answers.all()
        for problem_id in problems:
            for answer in answers:
                if answer.problem.id == problem_id:
                    row.append(answer.string_answer)
                    break
        writer.writerow(row)
    f.close()
    f = open('registration_receipts.csv', 'r')
    response = HttpResponse(f, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=registration_receipts.csv'
    return response


class RegistrationReceiptsAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'form',
                    'status', 'is_participating', 'team']
    list_filter = ['form', 'status', 'is_participating']
    actions = [delete_registration_receipts, download_csv]

    def name(self, obj):
        return obj.user.full_name


class PlayerAdmin(admin.ModelAdmin):
    model = Player
    list_display = ['user', 'receipt', 'fsm', 'current_state', 'last_visit']
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

    def solution_csv(self, request, queryset):

        file = open('small-answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(
            ['problem_name', 'problem_body', 'text', 'submitted_by'])
        problem_obj = queryset[0]
        answers = SmallAnswer.objects.filter(problem=problem_obj)
        ctr = 0
        for i in answers:
            if ctr == 0:
                writer.writerow(
                    [i.problem.name, i.problem.text, i.text, i.submitted_by])

            else:
                writer.writerow([i.problem.name, None, i.text, i.submitted_by])

            ctr += 1

        file.close()

        f = open('small-answers.csv', 'r')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=small-answers.csv'
        return response

    actions = [solution_csv]


class BigAnswerProblemAdmin(admin.ModelAdmin):
    list_display = ['paper', 'widget_type', 'creator']
    list_filter = ['widget_type']
    search_fields = []

    def solution_csv(self, request, queryset):

        file = open('big-answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(
            ['problem_name', 'problem_body', 'text', 'submitted_by'])
        problem_obj = queryset[0]
        answers = BigAnswer.objects.filter(problem=problem_obj)
        ctr = 0
        for i in answers:
            if ctr == 0:
                writer.writerow(
                    [i.problem.name, i.problem.text, i.text, i.submitted_by])

            else:
                writer.writerow([i.problem.name, None, i.text, i.submitted_by])

            ctr += 1

        file.close()

        f = open('big-answers.csv', 'r')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=big-answers.csv'
        return response

    actions = [solution_csv]


@admin.register(AnswerSheet)
class AnswerSheetCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer_sheet_type']
    list_display_links = ['id', 'answer_sheet_type']
    list_filter = ['answer_sheet_type']
    search_fields = ['answer_sheet_type']


@admin.register(Problem)
class ProblemCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type',
                    'creator', 'is_required']
    list_display_links = ['id', 'paper', 'widget_type', 'creator']
    list_filter = ['widget_type', 'is_required']
    search_fields = []

    def download_final_answers_scores(self, request, queryset):
        score_types = set()
        problems = {}
        for p in queryset:
            answers = []
            score_types |= set(
                st for st in p.paper.score_types.all().values_list('name', flat=True))
            for ans in p.answers.filter(is_final_answer=True):
                ans_dict = {'id': ans.id,
                            'first_name': ans.submitted_by.first_name,
                            'phone_number': ans.submitted_by.phone_number,
                            'last_name': ans.submitted_by.last_name,
                            'school': ans.submitted_by.school_studentship.school.name if ans.submitted_by.school_studentship.school else None,
                            'grade': ans.submitted_by.school_studentship.grade,
                            'province': ans.submitted_by.province,
                            'city': ans.submitted_by.city,
                            'gender': ans.submitted_by.gender,
                            'national_code': ans.submitted_by.national_code,
                            }
                for score in ans.scores.all():
                    ans_dict[score.type.name] = score.value
                answers.append(ans_dict)
            problems[p] = answers

        file = open('answers.csv', 'w', encoding="utf-8")
        writer = csv.writer(file)
        writer.writerow(
            ['problem_id', 'answer_id', 'first_name', 'last_name', 'phone_number', 'school', 'grade', 'province', 'city', 'gender',
             'national_code'] + [st for st in score_types])
        for p in queryset:
            for a in problems[p]:
                writer.writerow([p.id, a['id'], a['first_name'], a['last_name'], a['phone_number'], a['school'], a['grade'], a['province'],
                                 a['city'], a['gender'], a['national_code']] + [a.get(st, '') for st in score_types])
        file.close()

        f = open('answers.csv', 'rb')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=answers.csv'
        return response

    download_final_answers_scores.short_description = 'export scored answers'
    actions = [download_final_answers_scores]


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


class ChoiceInline(admin.TabularInline):
    model = Choice


@admin.register(MultiChoiceProblem)
class MultiChoiceProblemCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_display_links = ['id']
    list_filter = ['widget_type']
    search_fields = []
    inlines = [ChoiceInline]


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


def download_files_from_links(self, request, queryset):
    for media in queryset:
        try:
            if not media.file:
                link_file = get_django_file(media.link)
                media.file = link_file
                media.save()
        except:
            pass


@admin.register(Video)
class VideoCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'widget_type', 'creator']
    list_filter = []
    search_fields = []
    actions = [download_files_from_links]


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
    actions = [download_files_from_links]


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
admin.site.register(Widget, WidgetAdmin)
admin.site.register(UploadFileAnswer, UploadFileAnswerAdmin)
admin.site.register(Tag)


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
    search_fields = ('title',)


@admin.register(Placeholder)
class PlaceholderAdmin(admin.ModelAdmin):
    model = Placeholder
    list_display = ['id', 'name', 'title']
