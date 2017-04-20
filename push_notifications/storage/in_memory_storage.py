"""A local in-memory storage manager for users."""
import datetime
import threading
from push_notifications.storage import UserNotFoundException, \
    DuplicateUserException, GroupNotFoundException, \
    DuplicateGroupException


class InMemoryStorage:
    """Stores users only in memory with no persistence."""
    def __init__(self):
        self._users = {}
        self._groups = {}
        self._lock = threading.Lock()

    def register_user(self, username, access_token):
        """Register a new user.
        If the user already exists this will raise DuplicateUserException."""
        with self._lock:
            if username in self._users:
                raise DuplicateUserException(
                    "%s already registered" % username)
            self._users[username] = {
                "username": username,
                "accessToken": access_token,
                "creationTime": datetime.datetime.now(),
                "numOfNotificationsPushed": 0
            }
            return self._users[username]

    def get_users(self):
        """Get a list of all users."""
        return self._users.values()

    def get_by_username(self, username):
        """Get a user by username.
        If the user does not exist this will raise UserNotFoundException."""
        if username in self._users:
            return self._users[username]
        raise UserNotFoundException("%s does not exist" % username)

    def register_group(self, group_id, user_ids):
        """Register a group of users."""
        if group_id in self._groups:
            raise DuplicateGroupException(
                "%s is already registered" % group_id)
        for user_id in user_ids:
            if user_id not in self._users:
                raise UserNotFoundException("%s not found" % user_id)
        self._groups[group_id] = user_ids

    def get_group(self, group_id):
        """Get a group by group id."""
        if group_id in self._groups:
            return self._groups[group_id]
        raise GroupNotFoundException("%s does not exist" % group_id)

    def get_groups(self):
        """Return all groups."""
        return list(self._groups.values())

    def increment_notifications_pushed(self, username):
        """Increment numOfNotificationsPushed for the given user.
        If the user does not exist this will raise UserNotFoundException."""
        with self._lock:
            user = self.get_by_username(username)
            user["numOfNotificationsPushed"] += 1
            self._users[username] = user
        return user["numOfNotificationsPushed"]
