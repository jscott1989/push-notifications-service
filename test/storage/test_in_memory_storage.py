import unittest
from push_notifications.storage.in_memory_storage import InMemoryStorage
from push_notifications.storage import UserNotFoundException, \
    DuplicateUserException, GroupNotFoundException, DuplicateGroupException


class TestInMemoryStorage(unittest.TestCase):
    def setUp(self):
        self._storage = InMemoryStorage()

    def test_register_get(self):
        """Register and get a user."""
        self._storage.register_user("user1", "code1")
        self.assertEqual(len(self._storage.get_users()), 1)
        self._storage.register_user("user2", "code2")
        self.assertEqual(len(self._storage.get_users()), 2)
        self.assertEqual(self._storage.get_by_username("user1")["accessToken"],
                         "code1")
        self.assertEqual(self._storage.get_by_username("user2")["accessToken"],
                         "code2")

    def test_register_duplicate(self):
        """Register a duplicate user."""
        self._storage.register_user("user1", "code1")
        with self.assertRaises(DuplicateUserException):
            self._storage.register_user("user1", "code1")

    def test_increment_notifications(self):
        """Increment notifications."""
        self._storage.register_user("user1", "code1")
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
        self._storage.register_user("user1", "code1")
        self.assertEqual(len(self._storage.get_users()), 1)
        self._storage.register_user("user2", "code2")
        self.assertEqual(len(self._storage.get_users()), 2)

    def test_register_group(self):
        """Register a group."""
        self._storage.register_user("user1", "code1")
        self._storage.register_group("group1", ["user1"])
        self.assertEqual(self._storage.get_group("group1"), ["user1"])

    def test_group_not_found(self):
        """Get a group that isn't registered."""
        with self.assertRaises(GroupNotFoundException):
            self._storage.get_group("group1")

    def test_register_group_missing_user(self):
        """Register a group with a missing user."""
        with self.assertRaises(UserNotFoundException):
            self._storage.register_group("group1", "user1")

    def test_list_groups(self):
        """List groups."""
        self.assertEqual(len(self._storage.get_groups()), 0)
        self._storage.register_group("group1", [])
        self.assertEqual(len(self._storage.get_groups()), 1)
        self._storage.register_group("group2", [])
        self.assertEqual(len(self._storage.get_groups()), 2)

    def test_register_duplicate_group(self):
        """Register a duplicate group."""
        self._storage.register_group("group1", [])
        with self.assertRaises(DuplicateGroupException):
            self._storage.register_group("group1", [])
