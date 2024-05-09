from django.shortcuts import render

# Create your views here.
# emailsender/views.py

from django.core.mail import send_mail
from django.http import HttpResponse



from django.core.mail import EmailMessage



def send_email(request):
    subject = 'Hello from Sepid'
    message = 'This is a test email sent from Ehsan'
    from_email = 'your@example.com'  # Replace with your email address
    to_email = 'amoo.hashem.mehraban@gmail.com'  # Replace with recipient's email address

    send_mail(subject, message, from_email, [to_email])
    return  HttpResponse("goi")


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
