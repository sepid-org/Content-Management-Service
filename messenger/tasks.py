from celery import shared_task
from django.core.mail import EmailMessage


@shared_task()
def send_email_task(subject, recipients_emails, body):
    sender_email = 'sepid.org@gmail.com'
    mail = EmailMessage(subject=subject, body=body,
                        from_email=sender_email, to=recipients_emails)
    mail.content_subtype = 'html'
    try:
        mail.send()
        return True
    except:
        return False
