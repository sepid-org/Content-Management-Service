from rest_framework.exceptions import ParseError

from errors.error_codes import serialize_error


def multi_choice_answer_validator(choices, maximum_choices_could_be_chosen):
    if len(choices) > maximum_choices_could_be_chosen:
        raise ParseError(serialize_error('4019', {'maximum_choices_could_be_chosen': maximum_choices_could_be_chosen, 'len_choices': len(choices)},
                                         is_field_error=False))
    if len(choices) != len(set([choice['id'] for choice in choices])):
        raise ParseError(serialize_error('4020', is_field_error=False))
