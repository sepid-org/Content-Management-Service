from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from proxies.bank_service.main import BankProxy


@api_view(["GET"])
def get_currencies(request):
    website = request.headers.get('Website', None)
    bank_proxy = BankProxy(website)
    currencies = bank_proxy.get_currencies()
    return Response(currencies, status=status.HTTP_200_OK)
