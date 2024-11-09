from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from apps.fsm.models import Object
from proxies.bank_service.bank import get_user_balances
from proxies.bank_service.utils import transfer_funds_to_user
from .models import Spend
from django.core.exceptions import ObjectDoesNotExist


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def spend_on_object(request):
    """
    Endpoint to spend funds on an object.

    Expected request body:
    {
        "object_id": "123",
        "funds": {
            "gold": 100,
            "silver": 50,
            ...
        }
    }
    """
    try:
        # Validate request data
        object_id = request.data.get('object_id')
        funds = request.data.get('funds')

        if not object_id or not funds:
            return Response(
                {"error": "Both object_id and funds are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate object exists
        try:
            obj = Object.objects.get(id=object_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Object not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user has already spent on this object
        user_uuid = str(request.user.id)
        if Spend.objects.filter(user=user_uuid, object_id=obj.id).exists():
            return Response(
                {"error": "You have already spent on this object."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get user's current balance
        user_balances = get_user_balances(user_uuid)

        # Validate user has enough balance
        for currency, amount in funds.items():
            if user_balances.get(currency, 0) < amount:
                return Response(
                    {
                        "error": f"Insufficient {currency} balance",
                        "required": amount,
                        "available": user_balances.get(currency, 0)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            # Spending money
            website_name = request.headers.get('Website')
            response = transfer_funds_to_user(
                website_name=website_name,
                user_uuid=user_uuid,
                funds=funds,
            )

            # If transfer successful, create spend record
            spend = Spend.objects.create(
                user=user_uuid,
                object_id=obj.id,
                fund=funds,
                transaction_id=response.get('withdraw_transaction_id')
            )

            return Response({
                "message": "Successfully spent funds on object",
                "spend_id": spend.id,
                "transaction_id": spend.transaction_id,
                "spent_at": spend.spent_at,
                "funds": spend.fund
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
