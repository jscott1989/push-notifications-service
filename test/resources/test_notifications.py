from falcon import testing
import falcon
import json
from push_notifications import server
from push_notifications.storage.in_memory_storage import InMemoryStorage
from push_notifications.pushbullet_api import InvalidAccessTokenException
from unittest.mock import MagicMock
from unittest import mock


class TestNotifications(testing.TestCase):
    def setUp(self):
        self._storage = InMemoryStorage()
        self._pushbullet = MagicMock()
        self.app = server.setup_api(self._storage, self._pushbullet)

        self._storage.register_user("user1", "code1")
        self._storage.register_user("user2", "code2")
        self._storage.register_group("group1", ["user1"])
        self._storage.register_group("group2", ["user2"])

    def test_send_to_group(self):
        """Send to group using notifications api."""
        result = self.simulate_post("/v1/notifications", body=json.dumps({
                "groupIds": ["group1", "group2"],
                "title": "title",
                "body": "body"
            }))
        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(self._storage.get_by_username(
            "user1")["numOfNotificationsPushed"], 1)
        self.assertEqual(self._storage.get_by_username(
            "user2")["numOfNotificationsPushed"], 1)

    def test_send_to_duplicate_group(self):
        """Send to the same group twice."""
        result = self.simulate_post("/v1/notifications", body=json.dumps({
                "groupIds": ["group1", "group1"],
                "title": "title",
                "body": "body"
            }))
        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(len(result.json["errors"]), 0)
        self.assertEqual(self._storage.get_by_username(
            "user1")["numOfNotificationsPushed"], 1)
        self.assertEqual(self._storage.get_by_username(
            "user2")["numOfNotificationsPushed"], 0)

    def test_send_to_groups_with_same_users(self):
        """Send to two groups with the same users."""
        self._storage.register_group("group3", ["user1"])
        result = self.simulate_post("/v1/notifications", body=json.dumps({
                "groupIds": ["group1", "group3"],
                "title": "title",
                "body": "body"
            }))
        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(len(result.json["errors"]), 0)
        self.assertEqual(self._storage.get_by_username(
            "user1")["numOfNotificationsPushed"], 1)
        self.assertEqual(self._storage.get_by_username(
            "user2")["numOfNotificationsPushed"], 0)

    def test_failures(self):
        """Ensure that it responds with errors."""
        def raise_token_exception(a, b, c):
            raise InvalidAccessTokenException("Invalid token")

        self._pushbullet.create_push.side_effect = raise_token_exception

        result = self.simulate_post("/v1/notifications", body=json.dumps({
                "groupIds": ["group1", "group2"],
                "title": "title",
                "body": "body"
            }))
        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(len(result.json["errors"]), 2)
        self.assertEqual(self._storage.get_by_username(
            "user1")["numOfNotificationsPushed"], 0)
        self.assertEqual(self._storage.get_by_username(
            "user2")["numOfNotificationsPushed"], 0)
