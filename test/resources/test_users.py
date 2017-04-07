from falcon import testing
import falcon
import json
from push_notifications import server
import dateutil.parser
from datetime import datetime, timedelta
from push_notifications.storage.in_memory_storage import InMemoryStorage


class TestUsers(testing.TestCase):
    def setUp(self):
        self._storage = InMemoryStorage()
        self.app = server.setup_api(self._storage)

    def test_register_user(self):
        """Test registering a new user."""
        # Post a new user
        result = self.simulate_post('/v1/users', body=json.dumps(
            {"username": "testuser", "accessToken": "testtoken"}))
        creation_time = datetime.now()

        # Expect it to return HTTP 201
        self.assertEqual(result.status, falcon.HTTP_201)

        # The body should contain the created resource
        created_resource = result.json
        self.assertEqual(created_resource["username"], "testuser")
        self.assertEqual(created_resource["accessToken"], "testtoken")
        self.assertEqual(created_resource["numOfNotificationsPushed"], 0)
        created_time = dateutil.parser.parse(created_resource['creationTime'])
        self.assertLess(creation_time - created_time,
                        timedelta(milliseconds=100))

        # The location should point to the created resource
        result = self.simulate_get(result.headers['location'])
        self.assertEqual(result.status, falcon.HTTP_200)
        resource = result.json
        self.assertEqual(resource["username"], "testuser")
        self.assertEqual(resource["accessToken"], "testtoken")
        self.assertEqual(resource["numOfNotificationsPushed"], 0)
        created_time = dateutil.parser.parse(resource['creationTime'])
        self.assertLess(creation_time - created_time,
                        timedelta(milliseconds=100))

    def test_register_missing_username(self):
        """Register with a missing username."""
        result = self.simulate_post('/v1/users', body=json.dumps(
            {"accessToken": "testtoken"}))
        self.assertEqual(result.status, falcon.HTTP_400)

    def test_register_missing_access_token(self):
        """Register with a missing access token."""
        result = self.simulate_post('/v1/users', body=json.dumps(
            {"username": "testuser"}))
        self.assertEqual(result.status, falcon.HTTP_400)

    def test_register_duplicate_user(self):
        """Register the same user twice."""
        # Insert one validly
        self.simulate_post('/v1/users', body=json.dumps(
            {"username": "testuser", "accessToken": "testtoken"}))

        # Try to insert with the same username
        result = self.simulate_post('/v1/users', body=json.dumps(
            {"username": "testuser", "accessToken": "testtoken2"}))
        self.assertEqual(result.status, falcon.HTTP_400)

    def test_get_user(self):
        """Get a user."""
        creation_time = datetime.now()
        self._storage.register("testuser", "testtoken")
        result = self.simulate_get('/v1/users/testuser')
        self.assertEqual(result.status, falcon.HTTP_200)
        resource = result.json
        self.assertEqual(resource["username"], "testuser")
        self.assertEqual(resource["accessToken"], "testtoken")
        self.assertEqual(resource["numOfNotificationsPushed"], 0)
        created_time = dateutil.parser.parse(resource['creationTime'])
        self.assertLess(creation_time - created_time,
                        timedelta(milliseconds=100))

    def test_get_missing_user(self):
        """Get a user who is not registered."""
        result = self.simulate_get('/v1/users/testuser')
        self.assertEqual(result.status, falcon.HTTP_404)

    def test_list_users(self):
        """List users."""
        # First test getting an empty list
        result = self.simulate_get('/v1/users')
        self.assertEqual(result.json, [])

        self._storage.register("user1", "token1")
        result = self.simulate_get('/v1/users')
        self.assertEqual(len(result.json), 1)
        self.assertEqual(result.json[0]["accessToken"], "token1")
        self.assertEqual(result.json[0]["username"], "user1")

        self._storage.register("user2", "token2")
        result = self.simulate_get('/v1/users')
        self.assertEqual(len(result.json), 2)
        self.assertTrue(result.json[0]["username"] == "user1" or
                        result.json[1]["username"] == "user1")
        self.assertTrue(result.json[0]["username"] == "user2" or
                        result.json[1]["username"] == "user2")
