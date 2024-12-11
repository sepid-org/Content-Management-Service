from .base import IntrinsicAttribute


class Enabled(IntrinsicAttribute):
    pass


class Condition(IntrinsicAttribute):

    def is_true(self, *args, **kwargs):
        from apps.fsm.utils.utils import AnswerSheetFacade

        player = kwargs.get('player')
        user = kwargs.get('user')
        value = self.value
        total_condition_result = True

        if 'expected_correct_choices_in_last_answer_count' in value:
            if not player:
                total_condition_result = False
            else:
                expected_count = value.get(
                    'expected_correct_choices_in_last_answer_count')
                facade = AnswerSheetFacade(player.answer_sheet)
                total_condition_result = facade.check_expected_correct_choices_in_last_answer_count(
                    expected_count)

        if 'expected_choices' in value:
            if not player:
                total_condition_result = False
            else:
                expected_choice_ids = value.get('expected_choices')
                facade = AnswerSheetFacade(player.answer_sheet)
                total_condition_result = facade.check_expected_choices(
                    expected_choice_ids)

        if 'expected_choices_in_last_answer' in value:
            if not player:
                total_condition_result = False
            else:
                expected_choice_ids = value.get(
                    'expected_choices_in_last_answer')
                facade = AnswerSheetFacade(player.answer_sheet)
                total_condition_result = facade.check_expected_choices_in_last_answer(
                    expected_choice_ids)

        if 'completed_fsms' in value:
            completed_fsm_ids = value.get('completed_fsms')

            try:
                # Get distinct completed FSMs
                from apps.fsm.models import Player
                completed_fsm_count = Player.objects.filter(
                    user=user,
                    fsm__id__in=completed_fsm_ids,
                    finished_at__isnull=False
                ).values('fsm_id').distinct().count()

                # Compare with the total number of required unique FSMs
                total_condition_result = \
                    completed_fsm_count == len(set(completed_fsm_ids))
            except:
                total_condition_result = False

        is_not = value.get('not', False)
        return total_condition_result ^ is_not


class Cost(IntrinsicAttribute):
    pass


class Reward(IntrinsicAttribute):
    pass


class Default(IntrinsicAttribute):
    pass
