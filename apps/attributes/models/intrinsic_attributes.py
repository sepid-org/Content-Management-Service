from .base import IntrinsicAttribute


class Enabled(IntrinsicAttribute):

    def get_value(self, *args, **kwargs):
        return self.is_permitted(*args, **kwargs)


class Condition(IntrinsicAttribute):

    def is_true(self, *args, **kwargs):
        player = kwargs.get('player')
        value = self.value

        if 'completed_fsms' in value:
            completed_fsm_ids = value.get('completed_fsms')
            # Get distinct completed FSMs
            from apps.fsm.models import Player
            completed_fsm_count = Player.objects.filter(
                user=player.user,
                fsm__id__in=completed_fsm_ids,
                finished_at__isnull=False
            ).values('fsm_id').distinct().count()

            # Compare with the total number of required unique FSMs
            return completed_fsm_count == len(set(completed_fsm_ids))

        if 'expected_choices' in value:
            expected_choice_ids = value.get('expected_choices')

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
            return all(choice_id in all_choice_ids for choice_id in expected_choice_ids)

        if 'expected_choices_in_last_answer' in value:
            expected_choice_ids = value.get('expected_choices_in_last_answer')

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

                expected_choice_ids = set(expected_choice_ids)

                return submitted_choice_ids == expected_choice_ids

            except MultiChoiceAnswer.DoesNotExist:
                return False

        return True


class Funds(IntrinsicAttribute):
    pass
