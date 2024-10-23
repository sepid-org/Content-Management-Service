from .base import IntrinsicAttribute


class Condition(IntrinsicAttribute):

    def is_true(self, player):
        value = self.value

        if hasattr(value, 'expected_choices'):
            expected_choices = value.get('expected_choices')

            # Get all multi-choice answers in one query
            from apps.fsm.models.response import MultiChoiceAnswer
            multi_choice_answers = (
                player.answer_sheet.answers
                .instance_of(MultiChoiceAnswer)
                .prefetch_related('choices')
            )

            # Create a set of all selected choice IDs for O(1) lookup
            all_choice_ids = {
                choice.id
                for answer in multi_choice_answers
                for choice in answer.choices.all()
            }

            # Check if all expected choices exist in the set
            return all(choice_id in all_choice_ids for choice_id in expected_choices)

        if hasattr(value, 'expected_choices_in_last_answer'):
            expected_choices = value.get('expected_choices_in_last_answer')

            try:
                # Get the last multi-choice answer in a single query
                from apps.fsm.models.response import MultiChoiceAnswer
                last_answer = (
                    player.answer_sheet.answers
                    .instance_of(MultiChoiceAnswer)
                    .prefetch_related('choices')
                    .latest('id')
                )

                # Convert both sets of choices to sets for comparison
                submitted_choice_ids = {
                    choice.id for choice in last_answer.choices.all()}

                expected_choice_ids = set(expected_choices)

                return submitted_choice_ids == expected_choice_ids

            except MultiChoiceAnswer.DoesNotExist:
                return False

        return True


class Reward(IntrinsicAttribute):
    pass
