import logging

from django.conf import settings
from zeep import Client

from apps.accounts.models import Purchase
from errors.error_codes import serialize_error
from errors.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)

# ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
# ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
# ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

DEVELOPMENT_ZARINPAL_CONFIG = {
    'ROUTE_START_PAY': 'https://sandbox.zarinpal.com/pg/StartPay/',
    'ROUTE_WEB_GATE': 'https://sandbox.zarinpal.com/pg/services/WebGate/wsdl',
    'MERCHANT': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',  # Required
    'DESCRIPTION': ''  # Required
}

PRODUCTION_ZARINPAL_CONFIG = {
    'ROUTE_START_PAY': 'https://www.zarinpal.com/pg/StartPay/',
    'ROUTE_WEB_GATE': 'https://www.zarinpal.com/pg/services/WebGate/wsdl',
    'MERCHANT': '817461df-e332-4657-85d1-76e7e0a06f0e',  # Required
    'DESCRIPTION': ''  # Required
}

ZARINPAL_CONFIG = DEVELOPMENT_ZARINPAL_CONFIG if settings.SANDBOX else PRODUCTION_ZARINPAL_CONFIG


def send_request(amount, description, callback_url, email=None, mobile=None):
    client = Client(ZARINPAL_CONFIG['ROUTE_WEB_GATE'])
    result = client.service.PaymentRequest(
        ZARINPAL_CONFIG['MERCHANT'], amount, description, email, mobile, callback_url)
    if result.Status == 100:
        return f'{ZARINPAL_CONFIG["ROUTE_START_PAY"]}{str(result.Authority)}'
    else:
        logger.error(f'Zarinpal send request error: {result}')
        raise ServiceUnavailable(serialize_error('5001'))


def verify(status, authority, amount):
    client = Client(ZARINPAL_CONFIG['ROUTE_WEB_GATE'])
    if status == 'OK':
        result = client.service.PaymentVerification(
            ZARINPAL_CONFIG['MERCHANT'], authority, amount)
        if result.Status == 100:
            logger.info(f'Transaction success: {result}')
            return {
                'message': 'Success',
                'ref_id': str(result.RefID),
                'status': 200
            }
        elif result.Status == 101:
            logger.warning(f'Transaction submitted: {result}')
            return {
                'message': 'Repetitious',
                'ref_id': str(result.RefID),
                'status': 201
            }
        else:
            logger.warning(f'Zarinpal verification error: {result}')
            return {
                'message': 'Failed',
                'status': 400
            }
    else:
        logger.warning(
            f'Transaction failed or canceled by authority: {authority}')
        return {
            'message': 'Failed or canceled',
            'status': 403
        }


def get_payment_callback_url(purchase: Purchase, status: str = 'success') -> str:
    domain = purchase.callback_domain
    program = purchase.merchandise.program.slug
    status = status.lower()  # Ensure consistent case handling

    if status not in {'success', 'failure'}:
        raise ValueError("Status must be either 'success' or 'failure'")

    return f"http://{domain}/program/{program}/purchase/?status={status}&ref_id={purchase.ref_id}"
