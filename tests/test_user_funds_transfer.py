from proxies.bank_service.utils import deposit_funds_to_user


def test_transfer_funds_to_user_real_api():
    """Test transfer_funds_to_user with a real API call."""

    # Define test data
    website_name = "kamva"
    user_uuid = "9c82767b-9e2a-43cb-ad5c-52e498303042"
    funds = {"testi-coin": 100}

    # Call the function (real API call happens here)
    response = deposit_funds_to_user(website_name, user_uuid, funds)

    # Print response for debugging
    print("API Response:", response)

    # Assertions: Ensure the API returned expected fields
    assert "withdraw_transaction_id" in response
    assert "deposit_transaction_id" in response
    assert isinstance(response["withdraw_transaction_id"], str)
    assert isinstance(response["deposit_transaction_id"], str)
