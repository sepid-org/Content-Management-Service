from django.http import HttpResponse
from messenger.tasks import *
import os
from manage_content_service.settings.base import BASE_DIR


def send_email(request):
    html_content = os.path.join(BASE_DIR, "assets/greeting_mail.html")
    html_content = open(html_content, "r", encoding="utf-8").read()
    send_emailQeue.delay("ehsna", "ehsan.ghechisaz82@gmail.com",  html_content)
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
