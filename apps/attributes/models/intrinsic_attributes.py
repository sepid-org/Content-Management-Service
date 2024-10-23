from .base import IntrinsicAttribute


class Condition(IntrinsicAttribute):

    def is_true(self, player):
        value = self.value
        if hasattr(value, 'choices_must_have_been_selected'):
            choices_must_have_been_selected = value.get(
                'choices_must_have_been_selected')
            for choice_id in choices_must_have_been_selected:
                answer_sheet = player.answer_sheet
                # todo: check json condition in answer-sheet
                pass

        if hasattr(value, 'last_selected_choice'):
            last_selected_choice = value.get('last_selected_choice')
            for choice_id in choices_must_have_been_selected:
                # todo: check json condition in answer-sheet
                pass

        return True


class Reward(IntrinsicAttribute):
    pass
