from apps.fsm.models.response import MultiChoiceAnswer


class AnswerSheetFacade:
    def __init__(self, answer_sheet) -> None:
        self.answer_sheet = answer_sheet

    def _get_multi_choice_answers(self):
        return self.answer_sheet.answers.instance_of(MultiChoiceAnswer).prefetch_related('choices')

    def _get_last_multi_choice_answer(self):
        return self._get_multi_choice_answers().latest('created_at')

    def check_expected_choice(self, expected_choice_id: int):
        try:
            all_choice_ids = {
                choice.id
                for answer in self._get_multi_choice_answers()
                for choice in answer.choices.all()
            }
            return expected_choice_id in all_choice_ids
        except MultiChoiceAnswer.DoesNotExist:
            return False

    def check_expected_choices(self, expected_choice_ids: list[int]):
        try:
            all_choice_ids = {
                choice.id
                for answer in self._get_multi_choice_answers()
                for choice in answer.choices.all()
            }
            return all(expected_id in all_choice_ids for expected_id in expected_choice_ids)
        except MultiChoiceAnswer.DoesNotExist:
            return False

    def check_expected_choice_in_last_answer(self, expected_choice_id: int):
        try:
            last_answer = self._get_last_multi_choice_answer()
            return expected_choice_id in {choice.id for choice in last_answer.choices.all()}
        except MultiChoiceAnswer.DoesNotExist:
            return False

    def check_expected_choices_in_last_answer(self, expected_choice_ids: list[int]):
        try:
            last_answer = self._get_last_multi_choice_answer()
            submitted_choice_ids = {
                choice.id for choice in last_answer.choices.all()}
            return set(expected_choice_ids) == submitted_choice_ids
        except MultiChoiceAnswer.DoesNotExist:
            return False

    def check_expected_correct_choices_in_last_answer_count(self, expected_count: int):
        try:
            last_answer = self._get_last_multi_choice_answer()
            correct_choices_count = sum(
                1 for choice in last_answer.choices.all() if choice.is_correct)
            return correct_choices_count == expected_count
        except MultiChoiceAnswer.DoesNotExist:
            return False
