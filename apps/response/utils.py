from rest_framework.exceptions import ParseError

from errors.error_codes import serialize_error


class AnswerFacade:
    def __init__(self) -> None:
        pass

    def get_question(self, question_id: int):
        from apps.fsm.models.base import Widget
        return Widget.objects.filter(id=question_id).first()

    def submit_answer(self, user, player, provided_answer, question):
        from apps.fsm.models.response import Answer
        from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer

        # check if user has already answered this question correctly
        if question.correct_answer:
            user_correctly_answered_problems = Answer.objects.filter(
                submitted_by=user, is_correct=True)
            for answer in user_correctly_answered_problems:
                if answer.problem == question:
                    raise ParseError(serialize_error('6000'))

        # create submitted answer object
        serializer = AnswerPolymorphicSerializer(data={
            'is_final_answer': False,
            'problem': question.id,
            'submitted_by': user.id,
            **provided_answer
        })
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        # save answer in the player answer-sheet (if player exists):
        if player:
            answer_sheet = player.answer_sheet
            answer.answer_sheet = answer_sheet
            answer.save()
