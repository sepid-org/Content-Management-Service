import logging
import requests
from django.conf import settings
from apps.accounts.models import Purchase
from errors.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)
SANDBOX = settings.SANDBOX

subdomain = 'sandbox' if SANDBOX else 'payment'

# New Zarinpal URLs
ZP_API_REQUEST = f"https://{subdomain}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://{subdomain}.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = f"https://{subdomain}.zarinpal.com/pg/StartPay/"

# Zarinpal Configurations
ZARINPAL_CONFIG = {
    'MERCHANT': settings.ZARINPAL_MERCHANT_ID,
    'DESCRIPTION': 'Online Payment',
    'CURRENCY': 'IRR'
}

ERROR_MESSAGES = {
    -9: "Validation error.",
    -10: "Invalid merchant ID or IP address.",
    -11: "Merchant ID is not active.",
    -12: "Too many attempts, please try again later.",
    -15: "Payment gateway has been suspended.",
    -16: "Merchant verification level is below Silver.",
    -17: "Merchant has Blue-level restrictions.",
    -50: "Paid amount does not match the requested amount.",
    -51: "Unsuccessful payment.",
    -53: "Payment does not belong to this merchant ID.",
    -54: "Invalid authority.",
    -55: "Transaction not found.",
    101: "Transaction has been verified."
}


def send_request(amount, description, callback_url, email=None, mobile=None):
    """ Send payment request to Zarinpal """
    payload = {
        "merchant_id": ZARINPAL_CONFIG["MERCHANT"],
        "amount": amount,
        "callback_url": callback_url,
        "description": description,
        "currency": ZARINPAL_CONFIG["CURRENCY"],
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(ZP_API_REQUEST, json=payload, headers=headers)
        result = response.json()

        if response.status_code == 200 and result.get("data"):
            code = result["data"].get("code")
            if code == 100:
                return f'{ZP_API_STARTPAY}{result["data"]["authority"]}'
            else:
                error_message = ERROR_MESSAGES.get(
                    code, "An unknown error occurred.")
                raise ServiceUnavailable(error_message)
        else:
            raise ServiceUnavailable("Invalid response from Zarinpal.")
    except Exception as e:
        logger.exception("Error in send_request")
        raise ServiceUnavailable("Internal server error.")


def verify(status, authority, amount):
    """ Verify payment status in Zarinpal """
    if status != 'OK':
        logger.warning(
            f'Transaction failed or canceled. Authority: {authority}')
        return {"message": "Payment failed or canceled.", "status": 403}

    payload = {
        "merchant_id": ZARINPAL_CONFIG["MERCHANT"],
        "amount": amount,
        "authority": authority
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(ZP_API_VERIFY, json=payload, headers=headers)
        result = response.json()

        if response.status_code == 200 and result.get("data"):
            code = result["data"].get("code")
            if code == 100:
                return {"message": "Success", "ref_id": str(result["data"]["ref_id"]), "status": 200}
            elif code == 101:
                return {"message": "This transaction has already been verified.", "ref_id": str(result["data"]["ref_id"]), "status": 201}
            else:
                error_message = ERROR_MESSAGES.get(
                    code, "Unknown error in transaction verification.")
                return {"message": error_message, "status": 400}
        else:
            return {"message": "Invalid response from Zarinpal.", "status": 400}
    except Exception as e:
        logger.exception("Error in verify")
        raise ServiceUnavailable("Internal server error.")


def get_payment_callback_url(purchase: Purchase, status: str = 'success') -> str:
    """ Generate callback URL after payment """
    domain = purchase.callback_domain
    program = purchase.merchandise.program.slug
    status = status.lower()

    if status not in {'success', 'failure'}:
        raise ValueError("Status must be either 'success' or 'failure'.")

    return f"http://{domain}/program/{program}/purchase/?status={status}&ref_id={purchase.ref_id}"
