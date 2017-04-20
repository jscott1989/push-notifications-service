"""Resources relating to users."""

import logging
import falcon

from push_notifications.utils.json import json_dump
from push_notifications.utils.falcon import decode_json_request
from push_notifications.storage import UserNotFoundException, \
    DuplicateUserException
from push_notifications.pushbullet_api import InvalidAccessTokenException, \
    PushbulletException


def get_user(storage, username, logger=None):
    """Get a user from the given storage.
       This will raise a HTTPNotFound exception if the user is not found.
       """
    try:
        return storage.get_by_username(username)
    except UserNotFoundException:
        if logger:
            logger.error("User %s not found" % username)
        raise falcon.HTTPNotFound()


class UsersResource:
    """Resource representing the collection of users."""

    def __init__(self, storage):
        self._storage = storage
        self._logger = logging.getLogger('notifications_api.users')

    def on_post(self, req, resp):
        """Register a new user."""
        self._logger.info("New registration request")
        data = decode_json_request(req, ["username", "accessToken"])
        self._logger.info("Registration request for %s" % data["username"])
        try:
            user = self._storage.register_user(data["username"],
                                               data["accessToken"])
        except DuplicateUserException:
            self._logger.info(
                "Refused duplicate registration for %s" % data["username"])
            raise falcon.HTTPBadRequest()
        resp.body = json_dump(user)
        resp.status = falcon.HTTP_201
        resp.location = "/v1/users/%s" % user["username"]
        self._logger.info("Registration completed for %s" % data["username"])

    def on_get(self, req, resp):
        """List users."""
        self._logger.info("Listing users")
        resp.body = json_dump([u for u in self._storage.get_users()])


class UserResource:
    """Resource for manipulating a single user."""

    def __init__(self, storage):
        self._storage = storage
        self._logger = logging.getLogger('notifications_api.user')

    def on_get(self, req, resp, username):
        """Handles GET requests"""
        self._logger.info("Getting user info about %s" % username)
        user = get_user(self._storage, username, self._logger)
        resp.body = json_dump(user)


class UserNotificationsResource:
    def __init__(self, storage, pushbullet_api):
        self._storage = storage
        self._pushbullet_api = pushbullet_api
        self._logger = logging.getLogger(
            'notifications_api.user_notifications')

    def on_get(self, req, resp, username):
        """Return the number of notifications sent."""
        self._logger.info("Listing notification count for %s" % username)
        user = get_user(self._storage, username, self._logger)
        resp.body = json_dump({"numOfNotificationsPushed":
                               user["numOfNotificationsPushed"]})

    def on_post(self, req, resp, username):
        """Post a new notification."""
        self._logger.info("Posting new notification to %s" % username)
        user = get_user(self._storage, username, self._logger)
        access_token = user["accessToken"]

        data = decode_json_request(req, ["title", "body"])
        try:
            self._pushbullet_api.create_push(access_token,
                                             data["title"], data["body"])
        except InvalidAccessTokenException:
            self._logger.error(
                "Invalid pushbullet access token %s" % access_token)
            raise falcon.HTTPForbidden("Incorrect access token")
        except PushbulletException as e:
            self._logger.error(
                "Pushbullet error %s" % str(e))
            raise falcon.HTTPInternalServerError
        num_notifications = self._storage.increment_notifications_pushed(
            username)

        self._logger.info("Notification pushed to %s" % username)
        resp.status = falcon.HTTP_201
        resp.body = json_dump({"numOfNotificationsPushed":
                               num_notifications})
