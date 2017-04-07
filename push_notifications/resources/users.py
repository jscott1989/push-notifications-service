"""Resources relating to users."""

import logging
import falcon

from push_notifications.utils.json import json_dump
from push_notifications.utils.falcon import decode_json_request
from push_notifications.storage import UserNotFoundException, \
    DuplicateUserException


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
            user = self._storage.register(data["username"],
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

    def _get_user(self, username):
        """Get a user from the given storage.
           This will raise a HTTPNotFound exception if the user is not found.
           """
        try:
            return self._storage.get_by_username(username)
        except UserNotFoundException:
            self._logger.error("User %s not found" % username)
            raise falcon.HTTPNotFound()

    def on_get(self, req, resp, username):
        """Handles GET requests"""
        self._logger.info("Getting user info about %s" % username)
        user = self._get_user(username)
        resp.body = json_dump(user)
