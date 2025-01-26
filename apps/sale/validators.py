from rest_framework import serializers

from errors.error_codes import serialize_error


def positive_integer_validator(integer):
    if integer >= 0 and (integer * 10) % 10 == 0:
        return integer
    else:
        raise serializers.ValidationError(serialize_error('4017'))


def price_validator(price):
    if positive_integer_validator(price) == price:
        if price % 1000 == 0:
            return price
        raise serializers.ValidationError(serialize_error('4018'))


def percentage_validator(number):
    if 0. <= number <= 1.:
        return number
    else:
        raise serializers.ValidationError(serialize_error('4037'))
