from django.utils.timezone import is_aware
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
import pandas as pd
from apps.accounts.models import Purchase
from apps.fsm.models import RegistrationReceipt, AnswerSheet, Widget, BigAnswer, BigAnswerProblem, MultiChoiceProblem, UploadFileProblem, SmallAnswerProblem, SmallAnswer, UploadFileAnswer, MultiChoiceAnswer
from django.utils.timezone import make_naive
from apps.file_storage.serializers.file_serializer import FileSerializer
from apps.report.utils import extract_content_from_html, gregorian_to_jalali


def _get_participants_excel_file(form_id):
    # Fetching data using ORM
    receipts = RegistrationReceipt.objects.filter(form_id=form_id).select_related(
        'user',
        'user__school_studentship',
        'user__school_studentship__school'
    )

    # Define headers
    headers = [
        "ID",
        "First Name",
        "Last Name",
        "Username",
        "Phone Number",
        "National Code",
        "School Name",
        "City",
        "Province",
        "Receipt Status",
        "Is Participating",
    ]

    # Collect data
    data = []
    for receipt in receipts:
        user = receipt.user
        school = user.school_studentship.school

        data.append({
            "ID": receipt.id,
            "First Name": user.first_name,
            "Lastname Name": user.last_name,
            "Username": user.username,
            "Phone Number": user.phone_number,
            "National Code": user.national_code,
            "School Name": school.name,
            "City": school.city,
            "Province": school.province,
            "Receipt Status": receipt.status,
            "Is Participating": "Yes" if receipt.is_participating else "No",
        })

    # Create DataFrame
    df = pd.DataFrame(data)
    df.columns = headers

    # Sort the DataFrame if needed
    df = df.sort_values("ID")

    # Save DataFrame to an Excel file in memory
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    # Create an in-memory file
    in_memory_file = SimpleUploadedFile(
        f"form_{form_id}_participants.xlsx", buffer.read(), content_type="application/vnd.ms-excel"
    )

    # Serialize and save the file
    file = FileSerializer(data={"file": in_memory_file})
    file.is_valid(raise_exception=True)
    file.save()

    return file.data


def _get_program_merchandises_purchases_file(form_id):
    # Fetch the required data using Django ORM
    purchases = (
        Purchase.objects.filter(
            merchandise__program__registration_form_id=form_id)
        .select_related(
            "user",
            "merchandise",
            "merchandise__program"
        )
        .values(
            "id",  # Purchase ID
            "user__first_name",
            "user__last_name",
            "user__username",
            "user__phone_number",
            "user__national_code",
            "merchandise__name",
            "merchandise__price",
            "merchandise__discounted_price",
            "merchandise__program__name",  # Program Name
            "amount",  # Purchase amount
            "status",
            "created_at",
        )
    )

    # Define headers for the Excel file
    headers = [
        "Purchase ID",
        "User First Name",
        "User Last Name",
        "Username",
        "Phone Number",
        "National Code",
        "Merchandise Name",
        "Merchandise Price",
        "Discounted Price",
        "Program Name",
        "Purchase Amount",
        "Purchase Status",
        "Created At",
    ]

    # Convert queryset to list of dictionaries for DataFrame
    data = list(purchases)

    # Ensure datetimes are timezone-naive
    for row in data:
        if "created_at" in row and is_aware(row["created_at"]):
            row["created_at"] = row["created_at"].astimezone(
                None).replace(tzinfo=None)

    # Create DataFrame
    if not data:
        # Create an empty DataFrame with only headers
        df = pd.DataFrame(columns=headers)
    else:
        df = pd.DataFrame(data)
        df.columns = headers

    # Save DataFrame to an Excel file in memory
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    # Create an in-memory file
    in_memory_file = SimpleUploadedFile(
        f"program_{form_id}_merchandises_purchases.xlsx",
        buffer.read(),
        content_type="application/vnd.ms-excel"
    )

    # Serialize and save the file
    file = FileSerializer(data={"file": in_memory_file})
    file.is_valid(raise_exception=True)
    file.save()

    return file.data


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
            "created At Hour": sheet.created_at.strftime('%H:%M'),
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
            answer_data[problem_column] = extract_content_from_html(
                answer.text)
        for answer in choices:
            answer_choice = answer.choices.all()
            problem_column = f'Problem {answer.problem.id}'
            answer_text = ""
            counter = 0
            for i in answer_choice:
                if counter == 0:
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
    df.columns = ['ID', 'کاربر', 'تاریخ ایجاد', 'زمان ساخت',
                  'تاریخ بروزرسانی', 'زمان بروزرسانی'] + list(problem_headers.values())
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
def get_participants(request):
    registration_form_id = request.GET.get('registration_form_id')
    file_content = _get_participants_excel_file(
        form_id=registration_form_id)
    return Response(file_content)


@api_view(["get"])
def get_program_merchandises_purchases(request):
    program_id = request.GET.get('program_id')
    # todo: this function should not get form_id. It should get program_id as input
    file_content = _get_program_merchandises_purchases_file(form_id=program_id)
    return Response(file_content)


@api_view(["get"])
def get_answer_sheets(request):
    form_id = request.GET.get("form_id")
    file_content = _get_answer_sheets_excel_file_by_form_id(form_id)
    return Response(file_content)
