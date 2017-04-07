import unittest
from push_notifications.storage.in_memory_storage import InMemoryStorage
from push_notifications.storage import UserNotFoundException, \
    DuplicateUserException


class TestInMemoryStorage(unittest.TestCase):
    def setUp(self):
        self._storage = InMemoryStorage()

    def test_register_get(self):
        """Register and get a user."""
        self._storage.register("user1", "code1")
        self.assertEqual(len(self._storage.get_users()), 1)
        self._storage.register("user2", "code2")
        self.assertEqual(len(self._storage.get_users()), 2)
        self.assertEqual(self._storage.get_by_username("user1")["accessToken"],
                         "code1")
        self.assertEqual(self._storage.get_by_username("user2")["accessToken"],
                         "code2")

    def test_register_duplicate(self):
        """Register a duplicate user."""
        self._storage.register("user1", "code1")
        with self.assertRaises(DuplicateUserException):
            self._storage.register("user1", "code1")

    def test_increment_notifications(self):
        """Increment notifications."""
        self._storage.register("user1", "code1")
        user = self._storage.get_by_username("user1")
        self.assertEqual(user["numOfNotificationsPushed"], 0)

        n = self._storage.increment_notifications_pushed("user1")
        self.assertEqual(n, 1)
        user = self._storage.get_by_username("user1")
        self.assertEqual(user["numOfNotificationsPushed"], 1)

        n = self._storage.increment_notifications_pushed("user1")
        self.assertEqual(n, 2)
        user = self._storage.get_by_username("user1")
        self.assertEqual(user["numOfNotificationsPushed"], 2)

    def test_not_found(self):
        """Get a not found user."""
        with self.assertRaises(UserNotFoundException):
            self._storage.get_by_username("test")

    def test_get_users(self):
        """List users."""
        self.assertEqual(len(self._storage.get_users()), 0)
        self._storage.register("user1", "code1")
        self.assertEqual(len(self._storage.get_users()), 1)
        self._storage.register("user2", "code2")
        self.assertEqual(len(self._storage.get_users()), 2)
