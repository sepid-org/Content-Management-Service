from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import EmailMessage


@shared_task()
def send_emailQeue(name, emailAddress , html_file):
    subject = 'Hello from Sepid'
    message = 'This is a test email sent from Ehsan'
    from_email = name # Replace with your email address
    to_email = emailAddress # Replace with recipient's email address

    mail = EmailMessage(subject=subject,body=html_file, from_email=from_email, to=[to_email])
    mail.content_subtype = 'html'
    try:

        mail.send()
        return True
    except:
        return False