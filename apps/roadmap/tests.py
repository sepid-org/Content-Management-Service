from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from apps.roadmap.views import (
    get_player_taken_path,
    get_fsm_roadmap,
    _get_fsm_links,
    _get_player_taken_path,
    _get_previous_taken_state
)


class YourViewTests(TestCase):
    def setUp(self):
        pass

    def test_get_player_taken_path(self):
        with patch('apps.roadmap.views.Player.get_player') as mocked_get_player:
            player_instance = MagicMock()
            player_instance.current_state.fsm = MagicMock()
            mocked_get_player.return_value = player_instance

            # Mocking _get_previous_taken_state
            with patch('apps.roadmap.views._get_previous_taken_state') as mocked_prev_taken_state:
                mocked_prev_taken_state.return_value = None


                data = {'player_id': 1}
                request = APIRequestFactory().post('get_player_taken_path/', data)
                response = get_player_taken_path(request)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_fsm_roadmap(self):
        with patch('apps.roadmap.views.FSM.get_fsm') as mocked_get_fsm, \
                patch('apps.roadmap.views._get_fsm_edges') as mocked_get_fsm_edges:
            fsm_instance = MagicMock()
            fsm_instance.first_state.name = "First State"
            mocked_get_fsm.return_value = fsm_instance
            mocked_get_fsm_edges.return_value = [MagicMock(tail=MagicMock(), head=MagicMock())]

            data = {'fsm_id': 1}
            request = APIRequestFactory().post('get_fsm_roadmap/', data)
            response = get_fsm_roadmap(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_get_fsm_links(self):
    #     # Mocking FSM.get_fsm and _get_fsm_edges
    #     with patch('your_app_name.views.FSM.get_fsm') as mocked_get_fsm, \
    #             patch('your_app_name.views._get_fsm_edges') as mocked_get_fsm_edges:
    #         fsm_instance = MagicMock()
    #         mocked_get_fsm.return_value = fsm_instance
    #         mocked_get_fsm_edges.return_value = [MagicMock(tail=MagicMock(), head=MagicMock())]
    #
    #         # Call the function
    #         links = _get_fsm_links(1)
    #
    #         # Assertions
    #         self.assertIsInstance(links, list)
    #         # Add more assertions as needed
    #
    # def test_get_previous_taken_state(self):
    #     # Mocking PlayerHistory model
    #     with patch('your_app_name.views.PlayerHistory') as mocked_player_history:
    #         player_history_instance = MagicMock()
    #         player_history_instance.reverse_enter = False
    #         player_history_instance.entered_by_edge = MagicMock()
    #         player_history_instance.entered_by_edge.tail = MagicMock()
    #         mocked_player_history.all.return_value = [player_history_instance]
    #
    #         # Call the function
    #         previous_state = _get_previous_taken_state(MagicMock(), [player_history_instance])
    #
    #         # Assertions
    #         self.assertIsNotNone(previous_state)
    #         # Add more assertions as needed
    #
