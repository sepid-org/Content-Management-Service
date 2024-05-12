from celery import shared_task
from django.core.mail import send_mail


@shared_task()
def send_emailQeue(name):
    subject = 'Hello from Sepid'
    message = 'This is a test email sent from Ehsan'
    from_email = 'your@example.com'  # Replace with your email address
    to_email = 'amoo.hashem.mehraban@gmail.com'  # Replace with recipient's email address

    send_mail(subject, message, from_email, [to_email])
    return True