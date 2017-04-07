"""A local in-memory storage manager for users."""
import datetime
from push_notifications.storage import UserNotFoundException, \
    DuplicateUserException

# TODO: Deal with concurrency


class InMemoryStorage:
    """Stores users only in memory with no persistence."""
    def __init__(self):
        self._users = {}

    def register(self, username, access_token):
        """Register a new user.
        If the user already exists this will raise DuplicateUserException."""
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

    def increment_notifications_pushed(self, username):
        """Increment numOfNotificationsPushed for the given user.
        If the user does not exist this will raise UserNotFoundException."""
        user = self.get_by_username(username)
        user["numOfNotificationsPushed"] += 1
        self._users[username] = user
        return user["numOfNotificationsPushed"]
