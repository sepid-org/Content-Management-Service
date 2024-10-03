from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
import pandas as pd
from django.conf import settings
from apps.fsm.models.form import AnswerSheet
from apps.fsm.models.question_widget import Widget
from apps.fsm.models.question_widget import BigAnswer, BigAnswerProblem, MultiChoiceProblem, UploadFileProblem, SmallAnswerProblem, SmallAnswer ,UploadFileAnswer , Choice , MultiChoiceAnswer
from django.utils.timezone import make_naive
from apps.file_storage.serializers.file_serializer import FileSerializer
from apps.reports.utils import extract_content_from_html, gregorian_to_jalali
from proxies.metabase.main import MetabaseProxy

url = settings.METABASE_URL

Metabase_proxy = MetabaseProxy()


def _get_registration_receipts_excel_file(form_id):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "query": '{"query":{"source-table":60,"joins":[{"fields":[["field",143,{"join-alias":"Accounts+User+-+User"}],["field",142,{"join-alias":"Accounts+User+-+User"}],["field",156,{"join-alias":"Accounts+User+-+User"}],["field",158,{"join-alias":"Accounts+User+-+User"}],["field",144,{"join-alias":"Accounts+User+-+User"}],["field",161,{"join-alias":"Accounts+User+-+User"}],["field",159,{"join-alias":"Accounts+User+-+User"}],["field",146,{"join-alias":"Accounts+User+-+User"}],["field",147,{"join-alias":"Accounts+User+-+User"}],["field",152,{"join-alias":"Accounts+User+-+User"}],["field",154,{"join-alias":"Accounts+User+-+User"}],["field",153,{"join-alias":"Accounts+User+-+User"}]],"source-table":32,"condition":["=",["field",443,null],["field",151,{"join-alias":"Accounts+User+-+User"}]],"alias":"Accounts+User+-+User"},{"fields":"none","source-table":35,"condition":["=",["field",446,null],["field",271,{"join-alias":"Fsm+Answersheet+-+Answersheet+Ptr"}]],"alias":"Fsm+Answersheet+-+Answersheet+Ptr"},{"fields":"none","source-table":106,"condition":["=",["field",271,{"join-alias":"Fsm+Answersheet+-+Answersheet+Ptr"}],["field",269,{"join-alias":"Fsm+Answer"}]],"alias":"Fsm+Answer"},{"fields":[],"source-table":96,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",449,{"join-alias":"Fsm+Smallanswer"}]],"alias":"Fsm+Smallanswer"},{"fields":[],"source-table":46,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",288,{"join-alias":"Fsm+Biganswer"}]],"alias":"Fsm+Biganswer"},{"fields":"none","source-table":9,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",371,{"join-alias":"Fsm+Multichoiceanswer+Choices"}]],"alias":"Fsm+Multichoiceanswer+Choices"},{"fields":[],"source-table":66,"condition":["=",["field",372,{"join-alias":"Fsm+Multichoiceanswer+Choices"}],["field",300,{"join-alias":"Fsm+Choice+-+Choice"}]],"alias":"Fsm+Choice+-+Choice"},{"fields":[],"source-table":107,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",466,{"join-alias":"Fsm+Uploadfileanswer"}]],"alias":"Fsm+Uploadfileanswer"},{"fields":[["field",133,{"join-alias":"Accounts+Schoolstudentship"}]],"source-table":31,"condition":["=",["field",151,{"join-alias":"Accounts+User+-+User"}],["field",131,{"join-alias":"Accounts+Schoolstudentship"}]],"alias":"Accounts+Schoolstudentship"},{"fields":[["field",96,{"join-alias":"Accounts+Educationalinstitute+-+School"}],["field",93,{"join-alias":"Accounts+Educationalinstitute+-+School"}],["field",99,{"join-alias":"Accounts+Educationalinstitute+-+School"}]],"source-table":98,"condition":["=",["field",129,{"join-alias":"Accounts+Schoolstudentship"}],["field",84,{"join-alias":"Accounts+Educationalinstitute+-+School"}]],"alias":"Accounts+Educationalinstitute+-+School"}],"expressions":{"answer":["concat",["field",451,{"join-alias":"Fsm+Smallanswer"}],["field",290,{"join-alias":"Fsm+Biganswer"}],["field",303,{"join-alias":"Fsm+Choice+-+Choice"}],["field",467,{"join-alias":"Fsm+Uploadfileanswer"}]]},"fields":[["field",444,null],["expression","answer"]],"filter":["=",["field",779,null],'+f'{form_id}'+']},"type":"query","database":2,"middleware":{"js-int-to-string?":true,"add-default-userland-constraints?":true}}'
    }
    response = Metabase_proxy.post(f'{url}api/dataset/xlsx', headers, data)

    if response.status_code == 200:
        in_memory_file = SimpleUploadedFile(
            f"form{form_id}-respondents-answers.xlsx", response.content)
        file = FileSerializer(data={"file": in_memory_file})
        file.is_valid(raise_exception=True)
        file.save()
        print("File created successfully:")
        return file.data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")


def _get_program_merchandises_purchases_file(form_id):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "query": '{"database":2,"type":"query","query":{"source-table":104,"joins":[{"strategy":"left-join","alias":"Accounts+Merchandise+-+Merchandise","fields":[["field",103,{"base-type":"type/Text","join-alias":"Accounts+Merchandise+-+Merchandise"}],["field",105,{"base-type":"type/Integer","join-alias":"Accounts+Merchandise+-+Merchandise"}],["field",107,{"base-type":"type/Integer","join-alias":"Accounts+Merchandise+-+Merchandise"}]],"condition":["=",["field",123,{"base-type":"type/UUID"}],["field",106,{"base-type":"type/UUID","join-alias":"Accounts+Merchandise+-+Merchandise"}]],"source-table":73},{"strategy":"left-join","alias":"Accounts+User+-+User","fields":[["field",142,{"base-type":"type/Text","join-alias":"Accounts+User+-+User"}],["field",156,{"base-type":"type/Text","join-alias":"Accounts+User+-+User"}],["field",158,{"base-type":"type/Text","join-alias":"Accounts+User+-+User"}],["field",144,{"base-type":"type/Text","join-alias":"Accounts+User+-+User"}],["field",146,{"base-type":"type/Text","join-alias":"Accounts+User+-+User"}]],"condition":["=",["field",121,{"base-type":"type/UUID"}],["field",151,{"base-type":"type/UUID","join-alias":"Accounts+User+-+User"}]],"source-table":32},{"strategy":"left-join","alias":"Fsm+Program+-+Program","fields":"none","condition":["=",["field",786,{"base-type":"type/Integer","join-alias":"Accounts+Merchandise+-+Merchandise"}],["field",742,{"base-type":"type/Integer","join-alias":"Fsm+Program+-+Program"}]],"source-table":145}],"fields":[["field",116,{"base-type":"type/Integer"}],["field",114,{"base-type":"type/Text"}],["field",115,{"base-type":"type/DateTimeWithLocalTZ"}]],"filter":["=",["field",438,{"base-type":"type/Integer","source-field":762}],'+f'{form_id}'+']},"middleware":{"js-int-to-string?":true,"userland-query?":true,"add-default-userland-constraints?":true}}'
    }
    response = Metabase_proxy.post(f'{url}api/dataset/xlsx', headers, data)

    if response.status_code == 200:
        in_memory_file = SimpleUploadedFile(
            f"program{form_id}-merchandises-purchases.xlsx", response.content)
        file = FileSerializer(data={"file": in_memory_file})
        file.is_valid(raise_exception=True)
        file.save()
        print("File created successfully:")
        return file.data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")


def _get_answer_sheets_excel_file_by_form_id(form_id):
    answer_sheets = AnswerSheet.objects.filter(form__id=form_id)

    widgets = Widget.objects.filter(
        paper__id=form_id,
        widget_type__in=[
            Widget.WidgetTypes.SmallAnswerProblem,
            Widget.WidgetTypes.BigAnswerProblem,
            Widget.WidgetTypes.MultiChoiceProblem,
            Widget.WidgetTypes.UploadFileProblem
        ]
    )

    data = []

    problem_headers = {}
    problems = []
    for widget in widgets:
        if widget.widget_type == Widget.WidgetTypes.SmallAnswerProblem:
            problems += SmallAnswerProblem.objects.filter(pk=widget.id)
        elif widget.widget_type == Widget.WidgetTypes.BigAnswerProblem:
            problems += BigAnswerProblem.objects.filter(pk=widget.id)
        elif widget.widget_type == Widget.WidgetTypes.MultiChoiceProblem:
            problems += MultiChoiceProblem.objects.filter(pk=widget.id)
        elif widget.widget_type == Widget.WidgetTypes.UploadFileProblem:
            problems += UploadFileProblem.objects.filter(pk=widget.id)
        else:
            continue
    sorted_problems = sorted(problems, key=lambda p: p.order, reverse=True)
    for problem in sorted_problems:
        problem_headers[f'Problem {problem.id}'] = extract_content_from_html(
            problem.text)

    for sheet in answer_sheets:
        answer_data = {
            'ID': sheet.id,
            'User': sheet.user.username if sheet.user else None,
            'Created At': gregorian_to_jalali(str(make_naive(sheet.created_at))),
            "created At Hour" :sheet.created_at.strftime('%H:%M'),
            'Updated At': gregorian_to_jalali(str(make_naive(sheet.updated_at))),
            "Updated At Hour": sheet.updated_at.strftime('%H:%M'),
        }
        for problem_header in problem_headers:
            answer_data[problem_header] = None

        small_answers = SmallAnswer.objects.filter(answer_sheet=sheet)
        big_answers = BigAnswer.objects.filter(answer_sheet=sheet)
        choices = MultiChoiceAnswer.objects.filter(answer_sheet=sheet)
        files = UploadFileAnswer.objects.filter(answer_sheet=sheet)
        for answer in small_answers:
            problem_column = f'Problem {answer.problem.id}'
            answer_data[problem_column] = answer.text

        for answer in big_answers:
            problem_column = f'Problem {answer.problem.id}'
            answer_data[problem_column] = extract_content_from_html(answer.text)
        for answer in choices:
            answer_choice = answer.choices.all()
            problem_column = f'Problem {answer.problem.id}'
            answer_text = ""
            counter = 0
            for i in answer_choice:
                if counter == 0 :
                    answer_text += str(i)
                else:
                    answer_text += "\n" + str(i)
                counter += 1
            answer_data[problem_column] = answer_text
        for answer in files:
            problem_column = f'Problem {answer.problem.id}'
            answer_data[problem_column] = answer.answer_file

        data.append(answer_data)

    df = pd.DataFrame(data)
    df.columns = ['ID', 'کاربر', 'تاریخ ایجاد','زمان ساخت',
                  'تاریخ بروزرسانی','زمان بروزرسانی'] + list(problem_headers.values())
    df = df.sort_values('ID')
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    in_memory_file = SimpleUploadedFile(
        f"form_{form_id}_answers.xlsx", buffer.read(), content_type='application/vnd.ms-excel')
    file = FileSerializer(data={"file": in_memory_file})
    file.is_valid(raise_exception=True)
    file.save()
    return file.data


@api_view(["get"])
def get_registration_receipts(request):
    registration_form_id = request.GET.get('registration_form_id')
    file_content = _get_registration_receipts_excel_file(form_id=registration_form_id)
    return Response(file_content)


@api_view(["get"])
def get_program_merchandises_purchases(request):
    program_id = request.GET.get('program_id')
    # todo: EHSAN: this function should not get form_id. It should get program_id as input
    file_content = _get_program_merchandises_purchases_file(form_id=program_id)
    return Response(file_content)


@api_view(["get"])
def get_answer_sheets(request):
    form_id = request.GET.get("form_id")
    file_content = _get_answer_sheets_excel_file_by_form_id(form_id)
    return Response(file_content)
