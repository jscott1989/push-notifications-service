"""Resources relating to notifications."""

import logging
import falcon
from push_notifications.utils.falcon import decode_json_request
from push_notifications.utils.json import json_dump
from push_notifications.storage import GroupNotFoundException
from push_notifications.utils.notifications import send_notification_to_user


def get_group(storage, group_id, logger):
    try:
        user_ids = storage.get_group(group_id)
    except GroupNotFoundException:
        logger.info("Group not found")
        raise falcon.HTTPNotFound()
    return user_ids


class NotificationsResource:
    """Resource representing notifications."""

    def __init__(self, storage, pushbullet_api):
        self._storage = storage
        self._pushbullet_api = pushbullet_api
        self._logger = logging.getLogger('notifications_api.notifications')

    def on_post(self, req, resp):
        """Create a group."""
        self._logger.info("Sending notifications")
        data = decode_json_request(req, ["groupIds", "title", "body"])

        users = set()
        errors = []

        for group_id in data["groupIds"]:
            try:
                users.update(self._storage.get_group(group_id))
            except GroupNotFoundException:
                self._logger.info(
                    "Group Not Found %s" % group_id)
                errors.append("%s: Group Not Found" % group_id)

        for user in users:
            success, error = send_notification_to_user(self._pushbullet_api,
                                                       self._storage,
                                                       self._logger,
                                                       user,
                                                       data["title"],
                                                       data["body"])
            if not success:
                errors.append(error)

        resp.body = json_dump({
            "errors": errors
            })
        resp.status = falcon.HTTP_201
