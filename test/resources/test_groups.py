from falcon import testing
import falcon
import json
from push_notifications import server
from push_notifications.storage.in_memory_storage import InMemoryStorage
from push_notifications.pushbullet_api import InvalidAccessTokenException
from unittest.mock import MagicMock


class TestGroups(testing.TestCase):
    def setUp(self):
        self._storage = InMemoryStorage()
        self._pushbullet = MagicMock()
        self.app = server.setup_api(self._storage, self._pushbullet)

        self._storage.register_user("user1", "code1")

    def test_list_groups(self):
        """List groups."""
        result = self.simulate_get("/v1/groups")
        self.assertEqual(len(result.json), 0)

        self._storage.register_group("group1", ["user1"])

        result = self.simulate_get("/v1/groups")
        self.assertEqual(len(result.json), 1)
        self.assertEqual(result.json[0], ["user1"])

    def test_register_group(self):
        """Register group."""
        result = self.simulate_post("/v1/groups", body=json.dumps({
            "groupId": "group1",
            "users": ["user1"]
            }))

        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(self._storage.get_group("group1"), ["user1"])

    def test_register_duplicate_group(self):
        """Register groups with same id."""
        result = self.simulate_post("/v1/groups", body=json.dumps({
            "groupId": "group1",
            "users": ["user1"]
            }))
        self.assertEqual(result.status, falcon.HTTP_201)

        result = self.simulate_post("/v1/groups", body=json.dumps({
            "groupId": "group1",
            "users": ["user1"]
            }))
        self.assertEqual(result.status, falcon.HTTP_400)

    def test_register_group_missing_user(self):
        """Register groups with missing user."""
        result = self.simulate_post("/v1/groups", body=json.dumps({
            "groupId": "group1",
            "users": ["user2"]
            }))
        self.assertEqual(result.status, falcon.HTTP_400)

    def test_send_notification(self):
        """Send a notification to a group."""
        self._storage.register_user("user2", "code2")
        self._storage.register_group("group1", ["user1", "user2"])
        result = self.simulate_post("/v1/groups/group1/notifications",
                                    body=json.dumps({
                                        "title": "testtitle",
                                        "body": "testbody"
                                    }))
        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(len(result.json["errors"]), 0)
        self.assertEqual(self._storage.get_by_username("user1")
                         ["numOfNotificationsPushed"], 1)
        self.assertEqual(self._storage.get_by_username("user2")
                         ["numOfNotificationsPushed"], 1)

    def test_send_notification_failure(self):
        """Send a notification to a group."""
        def raise_token_exception(a, b, c):
            raise InvalidAccessTokenException("Invalid token")

        self._pushbullet.create_push.side_effect = raise_token_exception
        self._storage.register_user("user2", "code2")
        self._storage.register_group("group1", ["user1", "user2"])
        result = self.simulate_post("/v1/groups/group1/notifications",
                                    body=json.dumps({
                                        "title": "testtitle",
                                        "body": "testbody"
                                    }))
        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(len(result.json["errors"]), 2)
        self.assertEqual(self._storage.get_by_username("user1")
                         ["numOfNotificationsPushed"], 0)
        self.assertEqual(self._storage.get_by_username("user2")
                         ["numOfNotificationsPushed"], 0)
