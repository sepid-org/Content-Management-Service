import logging
from abc import ABC, abstractmethod
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class AbstractSubmissionHandler(ABC):
    def __init__(self, user=None):
        self.user = user

    @abstractmethod
    def validate_submission(self, request, *args, **kwargs):
        pass

    @abstractmethod
    def prepare_submission_data(self, request, *args, **kwargs):
        pass

    @abstractmethod
    def save_submission(self, data, *args, **kwargs):
        pass

    @abstractmethod
    def perform_post_submission_actions(self, submission, request, *args, **kwargs):
        pass

    def get_response_data(self, submission):
        return {}

    @transaction.atomic
    def submit(self, request, *args, **kwargs):
        self.validate_submission(request, *args, **kwargs)
        submission_data = self.prepare_submission_data(
            request, *args, **kwargs)
        submission = self.save_submission(submission_data, *args, **kwargs)
        self.perform_post_submission_actions(
            submission, request, *args, **kwargs)
        return Response(data=self.get_response_data(submission), status=status.HTTP_201_CREATED)
