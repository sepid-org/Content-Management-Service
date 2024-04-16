import os
import django
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage_content_service.settings.development')

django.setup()
application = get_default_application()
