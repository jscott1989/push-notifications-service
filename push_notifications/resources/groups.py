"""Resources relating to groups."""

import logging
import falcon
from push_notifications.utils.falcon import decode_json_request
from push_notifications.utils.json import json_dump
from push_notifications.storage import DuplicateGroupException, \
    UserNotFoundException, GroupNotFoundException
from push_notifications.utils.notifications import send_notification_to_user


def get_group(storage, group_id, logger):
    try:
        user_ids = storage.get_group(group_id)
    except GroupNotFoundException:
        logger.info("Group not found")
        raise falcon.HTTPNotFound()
    return user_ids


class GroupsResource:
    """Resource representing a collection of groups."""

    def __init__(self, storage):
        self._storage = storage
        self._logger = logging.getLogger('notifications_api.groups')

    def on_get(self, req, resp):
        """List groups."""
        self._logger.info("Listing groups")
        resp.body = json_dump(self._storage.get_groups())

    def on_post(self, req, resp):
        """Create a group."""
        self._logger.info("Registering group")
        data = decode_json_request(req, ["groupId", "users"])
        try:
            self._storage.register_group(data["groupId"], data["users"])
        except DuplicateGroupException:
            self._logger.info(
                "Refused duplicate registration for %s" % data["groupId"])
            raise falcon.HTTPBadRequest()
        except UserNotFoundException as e:
            self._logger.info(
                "User not found %s" % e)
            raise falcon.HTTPBadRequest()
        resp.body = json_dump(self._storage.get_group(data["groupId"]))
        resp.status = falcon.HTTP_201
        resp.location = "/v1/groups/%s" % data["groupId"]


class GroupResource:
    """Resource for manipulating a single group."""

    def __init__(self, storage):
        self._storage = storage
        self._logger = logging.getLogger('notifications_api.user')

    def on_get(self, req, resp, group_id):
        """Handles GET requests"""
        self._logger.info("Getting group info about %s" % group_id)
        group = get_group(self._storage, group_id, self._logger)
        resp.body = json_dump(group)


class GroupNotificationsResource:
    """Resource representing a notification on a group."""

    def __init__(self, storage, pushbullet_api):
        self._storage = storage
        self._pushbullet_api = pushbullet_api
        self._logger = logging.getLogger('notifications_api.groups')

    def on_post(self, req, resp, group_id):
        """Create a notification for this group."""
        self._logger.info("Posting new notification to %s" % group_id)
        data = decode_json_request(req, ["title", "body"])
        user_ids = get_group(self._storage, group_id, self._logger)

        errors = []
        for user in user_ids:
            success, error = send_notification_to_user(self._pushbullet_api,
                                                       self._storage,
                                                       self._logger,
                                                       user,
                                                       data["title"],
                                                       data["body"])
            if not success:
                errors.append(error)

            resp.status = falcon.HTTP_201
            resp.body = json_dump({"errors": errors})
