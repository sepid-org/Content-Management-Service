import os
from django.http import HttpResponse
from messenger.tasks import send_email_task
from manage_content_service.settings.base import BASE_DIR


def send_email(request):
    html_content_path = os.path.join(BASE_DIR, "assets/greeting_mail.html")
    html_content = open(html_content_path, "r", encoding="utf-8").read()
    send_email_task.delay(
        "Email Subject", ["ehsan.ghechisaz82@gmail.com"], html_content)
    return HttpResponse("goi")


# def send_email(request):
#     subject = 'Subject of the email'
#     message = 'This is the message body.'
#     from_email = 'your_email@gmail.com'  # Sender's email address
#
#     # List of recipient email addresses
#     recipient_list = ['ehsan.ghechisaz82@gmail.com']
#
#     send_mail(subject, message, from_email, recipient_list)
#     return HttpResponse('Email sent successfully!')
