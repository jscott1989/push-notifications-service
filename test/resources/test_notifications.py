from falcon import testing
import falcon
import json
from push_notifications import server
from push_notifications.storage.in_memory_storage import InMemoryStorage
from unittest.mock import MagicMock


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
