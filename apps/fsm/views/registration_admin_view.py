import pandas as pd
import numpy as np
from threading import Thread

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.accounts.utils.user_management import create_or_get_user, find_user_in_website, update_or_create_team, update_or_create_registration_receipt
from apps.fsm.utils.utils import register_user_in_program
from apps.fsm.models import RegistrationForm, transaction
from apps.fsm.permissions import IsRegistrationFormModifier
from apps.fsm.serializers.serializers import BatchRegistrationSerializer


class RegistrationAdminViewSet(GenericViewSet):
    queryset = RegistrationForm.objects.all()
    serializer_class = BatchRegistrationSerializer
    permission_classes = [IsRegistrationFormModifier]
    my_tags = ['registration_form_admin']

    @action(detail=True, methods=['post'])
    def register_participants_via_list(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participants_list_file = pd.read_excel(
            request.FILES['file'], dtype=str).replace(np.nan, None)

        def long_task():
            website = request.headers.get('Website')

            for index, participant in participants_list_file.iterrows():
                # remove None fields
                participant = {
                    'is_temporary': True,
                    **{key: value for key,
                       value in participant.items() if value}
                }

                try:
                    registration_form = self.get_object()
                    participant = handle_user_name_while_registration(
                        participant)
                    participant_user_account, created = create_or_get_user(
                        user_data=participant, website=website)
                    receipt = update_or_create_registration_receipt(
                        participant_user_account, registration_form)
                    update_or_create_team(
                        participant.get('group_name'), participant.get('chat_room_link'), receipt, registration_form)
                except:
                    pass

        thread = Thread(target=long_task)
        thread.start()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def register_user_in_program(self, request, pk=None):
        website = request.headers.get('Website')
        username = request.data.get('username')
        user = find_user_in_website(
            user_data={'username': username},
            website=website,
            raise_exception=True,
        )
        register_user_in_program(user=user, program=self.get_object().program)
        return Response(status=status.HTTP_201_CREATED)


def handle_user_name_while_registration(user_data):
    if not user_data.get('first_name') and not user_data.get('last_name') and user_data.get('full_name'):
        full_name_parts = user_data['full_name'].split(' ')
        user_data['first_name'] = full_name_parts[0]
        user_data['last_name'] = ' '.join(full_name_parts[1:])
    return user_data
