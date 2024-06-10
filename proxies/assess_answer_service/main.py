

import json
import requests

from manage_content_service.settings.base import get_environment_var

url = get_environment_var(
    'ASSESS_ANSWER_SERVICE_URL', 'https://aas.sepid.org/')


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
            'text': correct_answer.string_answer,
        },
        'given_answer': {
            'answer_type': given_answer.answer_type,
            'text': given_answer.string_answer,
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
