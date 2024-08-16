

import json
from django.conf import settings
import requests

url = settings.ASSESS_ANSWER_SERVICE_URL


def assess_answer(question, given_answer):
    correct_answer = question.correct_answer
    if not question.correct_answer:
        raise Exception("no correct answer provided")
    body = {
        'question': {
            'question_type': question.widget_type,
        },
        'correct_answer': {
            'answer_type': question.correct_answer.answer_type,
            'string': correct_answer.string_answer,
        },
        'given_answer': {
            'answer_type': given_answer.answer_type,
            'string': given_answer.string_answer,
        }
    }
    correctness_percentage = -1
    comment = 'not assessed'
    try:
        response = requests.post(f'{url}facade/v1/assess/', json=body)
        result = json.loads(response.text)
        correctness_percentage = result.get('correctness_percentage')
        comment = result.get('comment')
    except:
        pass
    return [correctness_percentage, comment]
