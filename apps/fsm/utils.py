import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q

from apps.fsm.models import FSM, Edge


def _get_fsm_edges(fsm: FSM) -> list[Edge]:
    return Edge.objects.filter(Q(tail__fsm=fsm) | Q(head__fsm=fsm))


def get_django_file(url: str):
    r = requests.get(url, allow_redirects=True)

    if not r.ok:
        raise Exception("fail to fetch")

    file_name = url.rsplit('/', 1)[1]
    file_type = r.headers.get('content-type')
    file_size = int(r.headers.get('content-length'))

    file_io = BytesIO(r.content)

    django_file = InMemoryUploadedFile(
        file_io, None, file_name, file_type,  file_size, None)

    return django_file


class SafeTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request=request)
        except:
            return None
