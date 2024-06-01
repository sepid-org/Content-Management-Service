from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from unittest.mock import patch, MagicMock
from apps.roadmap.views import get_player_transited_path, get_fsm_roadmap


class TestRoadmapViewsHealthCheck(TestCase):
    def setUp(self):
        pass

    def test_get_player_transited_path(self):
        with patch('apps.roadmap.views.Player.get_player') as mocked_get_player:
            player_instance = MagicMock()
            player_instance.current_state.fsm = MagicMock()
            mocked_get_player.return_value = player_instance

            # Mocking _get_previous_taken_state
            with patch('apps.roadmap.views._get_previous_taken_state') as mocked_prev_taken_state:
                mocked_prev_taken_state.return_value = None

                data = {'player_id': 1}
                request = APIRequestFactory().post('get_player_transited_path/', data)
                response = get_player_transited_path(request)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_fsm_roadmap(self):
        with patch('apps.roadmap.views.FSM.get_fsm') as mocked_get_fsm, \
                patch('apps.roadmap.views._get_fsm_edges') as mocked_get_fsm_edges:
            fsm_instance = MagicMock()
            fsm_instance.first_state.name = "First State"
            mocked_get_fsm.return_value = fsm_instance
            mocked_get_fsm_edges.return_value = [
                MagicMock(tail=MagicMock(), head=MagicMock())]

            data = {'fsm_id': 1}
            request = APIRequestFactory().post('get_fsm_roadmap/', data)
            response = get_fsm_roadmap(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
