import logging
from abc import ABC, abstractmethod
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class AbstractSubmissionHandler(ABC):
    def __init__(self, user=None, player=None, website=None):
        self.user = user
        self.player = player
        self.website = website

    def validate_submission(self, data):
        pass

    def prepare_submission_data(self, data):
        pass

    def save_submission(self, validated_data):
        pass

    def perform_post_submission_actions(self):
        pass

    def get_response_data(self, submission):
        pass

    @transaction.atomic
    def submit(self, data):
        self.validate_submission(data)
        validated_data = self.prepare_submission_data(data)
        submission = self.save_submission(validated_data)
        self.perform_post_submission_actions()
        return Response(data=self.get_response_data(submission), status=status.HTTP_200_OK)
