import time
import logging
import xlsxwriter
from django.db.models import Prefetch
from django.utils.timezone import is_aware
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from apps.accounts.models import Purchase
from apps.fsm.models import RegistrationReceipt, Widget, Answer, Form, FSM, Player, BigAnswer, MultiChoiceAnswer, SmallAnswer, UploadFileAnswer
from django.utils.timezone import make_naive
from apps.file_storage.serializers.file_serializer import FileSerializer
from apps.report.utils import extract_content_from_html, gregorian_to_jalali


def _get_participants_excel_file(form_id):
    # Fetch ordered data using ORM
    receipts = RegistrationReceipt.objects.filter(
        form_id=form_id
    ).select_related(
        'user',
        'user__school_studentship',
        'user__school_studentship__school'
    ).order_by('id')

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

    # Create Excel file in memory
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()

    # Write headers
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Write data rows
    for row_num, receipt in enumerate(receipts, start=1):
        user = receipt.user
        school_studentship = getattr(user, 'school_studentship', None)
        school = school_studentship.school if school_studentship else None

        # Prepare row data according to headers order
        row_data = [
            receipt.id,
            user.first_name,
            user.last_name,
            user.username,
            user.phone_number,
            user.national_code,
            school.name if school else "-",
            getattr(user, 'city', ''),
            getattr(user, 'province', ''),
            receipt.status,
            "Yes" if receipt.is_participating else "No",
        ]

        # Write row to worksheet
        for col_num, value in enumerate(row_data):
            worksheet.write(row_num, col_num, value)

    # Finalize and prepare file
    workbook.close()
    buffer.seek(0)

    in_memory_file = SimpleUploadedFile(
        f"form_{form_id}_participants.xlsx",
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Serialize and save the file
    file_serializer = FileSerializer(data={"file": in_memory_file})
    file_serializer.is_valid(raise_exception=True)
    file_serializer.save()

    return file_serializer.data


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

    # Define headers and corresponding keys
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
    # Order of keys corresponding to the headers above
    keys = [
        "id",
        "ref_id",
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__phone_number",
        "user__national_code",
        "merchandise__name",
        "merchandise__price",
        "merchandise__discounted_price",
        "merchandise__program__name",
        "amount",
        "status",
        "created_at",
    ]

    # Convert queryset to list of dictionaries
    data = list(purchases)

    # Ensure datetimes are timezone-naive
    for row in data:
        if "created_at" in row and is_aware(row["created_at"]):
            row["created_at"] = row["created_at"].astimezone(
                None).replace(tzinfo=None)

    # Create an in-memory output file for the new workbook.
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
    worksheet = workbook.add_worksheet("Purchases")

    # Write header row
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Write data rows
    for row_num, row_data in enumerate(data, start=1):
        for col_num, key in enumerate(keys):
            # Write the cell value; if key is missing, it writes None.
            worksheet.write(row_num, col_num, row_data.get(key))

    workbook.close()
    buffer.seek(0)

    # Create an in-memory file for Django file handling
    in_memory_file = SimpleUploadedFile(
        f"program_{form_id}_merchandises_purchases.xlsx",
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Serialize and save the file
    file_serializer = FileSerializer(data={"file": in_memory_file})
    file_serializer.is_valid(raise_exception=True)
    file_serializer.save()

    return file_serializer.data


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


# Configure your logger as needed.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _get_answer_sheets_excel_file(questions, answer_sheets_queryset):
    overall_start = time.time()
    logger.info("Starting generation of answer sheets Excel file.")

    # Start timing for question headers generation
    headers_start = time.time()
    question_headers = {
        f'Problem {q.id}': extract_content_from_html(q.text)
        for q in sorted(questions, key=lambda p: p.order, reverse=True)
    }
    logger.info(
        f"Generated question headers in {time.time() - headers_start:.2f} seconds.")

    # Timing for prefetching related answers
    prefetch_start = time.time()
    answer_sheets_queryset = answer_sheets_queryset.prefetch_related(
        Prefetch(
            'answers',
            queryset=Answer.objects.filter(
                is_final_answer=True
            ).prefetch_related('choices'),
            to_attr='prefetched_answers'
        )
    )
    logger.info(
        f"Completed prefetch_related in {time.time() - prefetch_start:.2f} seconds.")

    # Prepare the workbook
    workbook_start = time.time()
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    headers = ['User ID', 'ID', 'کاربر', 'زمان ایجاد',
               'زمان بروزرسانی'] + list(question_headers.values())
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)
    logger.info(
        f"Worksheet headers written in {time.time() - workbook_start:.2f} seconds.")

    # Writing rows for each answer sheet
    row_start = time.time()
    row_num = 1
    total_answersheets = answer_sheets_queryset.count() if hasattr(
        answer_sheets_queryset, 'count') else len(answer_sheets_queryset)
    logger.info(f"Processing {total_answersheets} answer sheets.")

    for index, answer_sheet in enumerate(answer_sheets_queryset, start=1):
        row_data = [
            str(answer_sheet.user.id) if answer_sheet.user else None,
            answer_sheet.id,
            answer_sheet.user.username if answer_sheet.user else None,
            f"{gregorian_to_jalali(str(make_naive(answer_sheet.created_at)))} {answer_sheet.created_at.strftime('%H:%M')}",
            f"{gregorian_to_jalali(str(make_naive(answer_sheet.updated_at)))} {answer_sheet.updated_at.strftime('%H:%M')}"
        ]

        answer_dict = {}
        for ans in answer_sheet.prefetched_answers:
            problem_column = f'Problem {ans.problem.id}'
            if isinstance(ans, SmallAnswer) or isinstance(ans, BigAnswer):
                answer_dict[problem_column] = ans.text
            elif isinstance(ans, MultiChoiceAnswer):
                answer_dict[problem_column] = "\n".join(
                    str(choice) for choice in ans.choices.all())
            elif isinstance(ans, UploadFileAnswer):
                answer_dict[problem_column] = str(ans.answer_file)

        # Append answers for each question header
        row_data.extend(answer_dict.get(header, '')
                        for header in question_headers.keys())

        # Write row data
        for col_num, cell_value in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_value)
        row_num += 1

        # Log progress every 100 rows (or adjust as needed)
        if index % 100 == 0:
            logger.info(
                f"Processed {index} answer sheets in {time.time() - row_start:.2f} seconds.")

    logger.info(
        f"Finished processing rows in {time.time() - row_start:.2f} seconds.")

    # Finalize workbook and save file
    workbook_close_start = time.time()
    workbook.close()
    output.seek(0)
    logger.info(
        f"Workbook closed in {time.time() - workbook_close_start:.2f} seconds.")

    in_memory_file = SimpleUploadedFile(
        "answer_sheets.xlsx",
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    file_serializer = FileSerializer(data={"file": in_memory_file})
    file_serializer.is_valid(raise_exception=True)
    file_serializer.save()
    logger.info(
        f"File saved successfully in {time.time() - overall_start:.2f} seconds total.")

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
