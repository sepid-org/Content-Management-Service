from django.db.models import Prefetch
from django.utils.timezone import is_aware
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
import pandas as pd
from apps.accounts.models import Purchase
from apps.fsm.models import RegistrationReceipt, Widget, Answer, Form, FSM, Player
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
        "School",
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
            "School": school.name if school else "-",
            "City": user.city,
            "Province": user.province,
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
            "ref_id",
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
        "Reference ID",
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


def _get_answer_sheets_excel_file_by_fsm_id(fsm_id):
    fsm = FSM.objects.get(id=fsm_id)
    players = Player.objects.filter(fsm=fsm)
    answer_sheets = []
    for player in players:
        answer_sheets.append(player.answer_sheet)

    widgets = fsm.get_questions()

    return _get_answer_sheets_excel_file(widgets, answer_sheets)


def _get_answer_sheets_excel_file_by_form_id(form_id):
    form = Form.objects.get(id=form_id)
    # Use select_related for the answer_sheet's user to avoid extra queries.
    answer_sheets = form.answer_sheets.select_related('user')
    # Filter widgets to get only the ones that correspond to answer problems.
    questions = form.widgets.filter(
        widget_type__in=[
            Widget.WidgetTypes.SmallAnswerProblem,
            Widget.WidgetTypes.BigAnswerProblem,
            Widget.WidgetTypes.MultiChoiceProblem,
            Widget.WidgetTypes.UploadFileProblem
        ]
    )

    return _get_answer_sheets_excel_file(questions, answer_sheets)


def _get_answer_sheets_excel_file(questions, answer_sheets_queryset):
    # Build question headers from sorted questions.
    question_headers = {
        f'Problem {q.id}': extract_content_from_html(q.text)
        for q in sorted(questions, key=lambda p: p.order, reverse=True)
    }

    # Prefetch only final answers.
    # We rely on the polymorphic manager to return concrete subclass instances,
    # and prefetch_related 'choices' for multi-choice answers.
    answer_sheets_queryset = answer_sheets_queryset.prefetch_related(
        Prefetch(
            'answers',
            queryset=Answer.objects.filter(is_final_answer=True)
            .prefetch_related('choices'),
            to_attr='prefetched_answers'
        )
    )

    data = []
    for answer_sheet in answer_sheets_queryset:
        answer_sheet_data = {
            'User ID': answer_sheet.user.id if answer_sheet.user else None,
            'ID': answer_sheet.id,
            'User': answer_sheet.user.username if answer_sheet.user else None,
            'Created At': (
                f"{gregorian_to_jalali(str(make_naive(answer_sheet.created_at)))} "
                f"{answer_sheet.created_at.strftime('%H:%M')}"
            ),
            'Updated At': (
                f"{gregorian_to_jalali(str(make_naive(answer_sheet.updated_at)))} "
                f"{answer_sheet.updated_at.strftime('%H:%M')}"
            ),
        }
        # Initialize each question column with None.
        for header in question_headers:
            answer_sheet_data[header] = None

        # Iterate through the prefetched final answers.
        for answer in answer_sheet.prefetched_answers:
            # Here we assume that each concrete answer subclass has a field named "problem"
            # which is a ForeignKey to the corresponding widget (question).
            problem_column = f'Problem {answer.problem.id}'
            if answer.answer_type == Answer.AnswerTypes.SmallAnswer:
                answer_sheet_data[problem_column] = answer.text
            elif answer.answer_type == Answer.AnswerTypes.BigAnswer:
                answer_sheet_data[problem_column] = answer.text
            elif answer.answer_type == Answer.AnswerTypes.MultiChoiceAnswer:
                answer_sheet_data[problem_column] = "\n".join(
                    str(choice) for choice in answer.choices.all()
                )
            elif answer.answer_type == Answer.AnswerTypes.UploadFileAnswer:
                answer_sheet_data[problem_column] = answer.answer_file

        data.append(answer_sheet_data)

    # Create the DataFrame with fixed columns followed by question columns.
    df = pd.DataFrame(data)
    df.columns = (
        ['User ID', 'ID', 'کاربر', 'زمان ایجاد', 'زمان بروزرسانی'] +
        list(question_headers.values())
    )
    df = df.sort_values('ID')

    # Write the DataFrame to an Excel file in memory.
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    in_memory_file = SimpleUploadedFile(
        "answer_sheets.xlsx",
        buffer.read(),
        content_type='application/vnd.ms-excel'
    )
    file_serializer = FileSerializer(data={"file": in_memory_file})
    file_serializer.is_valid(raise_exception=True)
    file_serializer.save()
    return file_serializer.data


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
    fsm_id = request.GET.get("fsm_id")
    if form_id:
        file_content = _get_answer_sheets_excel_file_by_form_id(form_id)
    elif fsm_id:
        file_content = _get_answer_sheets_excel_file_by_fsm_id(fsm_id)
    return Response(file_content)
