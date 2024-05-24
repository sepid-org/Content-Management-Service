import os
from django.http import HttpResponse
from messenger.tasks import send_email_task
from manage_content_service.settings.base import BASE_DIR


import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        email_data = {
            "email": request.POST.get("email"),
            "subject": request.POST.get("subject"),
            "body": request.POST.get("body")
        }
        response = requests.post("http://127.0.0.1:8080/send-email/", json=email_data)

        if response.status_code == 200:
            return JsonResponse({"message": "Email has been sent"}, status=200)
        else:
            return JsonResponse({"error": "Failed to send email"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



# def send_email(request):
#     html_content =os.path.join(BASE_DIR, "assets/greeting_mail.html")
#     html_content= open(html_content, "r", encoding="utf-8").read()
#     send_emailQeue.delay("ehsna" , "ehsan.ghechisaz82@gmail.com" ,  html_content)
#     return  HttpResponse("goi")


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
