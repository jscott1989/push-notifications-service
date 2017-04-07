import unittest
import json
from push_notifications.pushbullet_api import PushbulletAPI, \
    InvalidAccessTokenException, PushbulletException
from unittest import mock
from unittest.mock import MagicMock


class TestPushbulletAPI(unittest.TestCase):

    def setUp(self):
        self._api = PushbulletAPI("https://api.pushbullet.com/v2")

    @mock.patch('requests.post')
    def test_create_push(self, post_mock):
        """Create a push."""
        post_mock.return_value = MagicMock(status_code=200)
        self._api.create_push("test_access_token", "test_title", "test_body")

        self.assertEqual(post_mock.call_args[0][0],
                         'https://api.pushbullet.com/v2/pushes')

        request_data = json.loads(post_mock.call_args[0][1])

        self.assertEqual(request_data["body"], 'test_body', )
        self.assertEqual(request_data["title"], 'test_title')
        self.assertEqual(post_mock.call_args[1]["headers"]["Access-Token"],
                         'test_access_token')

    @mock.patch('requests.post')
    def test_invalid_token(self, post_mock):
        """A push with invalid token raises exception."""
        post_mock.return_value = MagicMock(
            status_code=401,
            json=lambda: {"error": {"message": "Authentication error"}})

        with self.assertRaises(InvalidAccessTokenException):
            self._api.create_push(
                "test_access_token", "test_title", "test_body")

    @mock.patch('requests.post')
    def test_unknown_error(self, post_mock):
        """An unknown error raises exception."""
        post_mock.return_value = MagicMock(
            status_code=404,
            json=lambda: {"error": {"message": "Error"}})

        with self.assertRaises(PushbulletException):
            self._api.create_push(
                "test_access_token", "test_title", "test_body")
