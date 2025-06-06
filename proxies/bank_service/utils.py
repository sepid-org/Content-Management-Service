from proxies.bank_service.bank import request_transfer
from typing import TypedDict


class TransferResponse(TypedDict):
    withdraw_transaction_id: str
    deposit_transaction_id: str


def transfer_funds_to_user(website_uuid: str, user_uuid: str, funds: dict) -> TransferResponse:

    return request_transfer(
        sender_id=website_uuid,
        receiver_id=str(user_uuid),
        funds=funds,
    )


def transfer_funds_from_user(website_uuid: str, user_uuid: str, funds: dict) -> TransferResponse:

    return request_transfer(
        sender_id=str(user_uuid),
        receiver_id=website_uuid,
        funds=funds,
    )
