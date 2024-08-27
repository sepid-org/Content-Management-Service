

import json
from django.conf import settings
import requests

url = settings.ASSESS_ANSWER_SERVICE_URL

type_caster = {
    "SmallAnswer": "Small",
    "BigAnswer": "Long",
    "MultiChoiceAnswer": "MultiChoiceAnswer",
    "UploadFileAnswer": "UploadFile",
}


def assess_answer(question, given_answer):
    correct_answer = question.correct_answer
    if not question.correct_answer:
        raise Exception("no correct answer provided")
    body = {
        'question': question.text,
        'context': {
            'correct_answer': correct_answer.string_answer,
        },
        'proposed_answer': {
            'type': type_caster[given_answer.answer_type],
            'text': given_answer.string_answer,
        }
    }
    score = -1
    feedback = 'not assessed'
    improvement_suggestion = 'not assessed'
    try:
        response = requests.post(f'{url}facade/v1/assess/', json=body)
        result = json.loads(response.text)
        score = result.get('score')
        feedback = result.get('feedback')
        improvement_suggestion = result.get('improvement_suggestion')
    except:
        pass
    return [score, feedback, improvement_suggestion]
