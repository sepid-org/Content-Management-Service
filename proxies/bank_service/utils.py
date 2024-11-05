from proxies.bank_service.bank import request_transfer
from proxies.website_service.main import get_website
from typing import TypedDict


class TransferResponse(TypedDict):
    withdraw_transaction_id: str
    deposit_transaction_id: str


def transfer_funds_to_user(website_name, user_uuid, funds) -> TransferResponse:
    website = get_website(website_name)

    return request_transfer(
        sender_id=website.get('uuid'),
        receiver_id=str(user_uuid),
        funds=funds,
    )
