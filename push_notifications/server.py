"""A simple Notification Server."""

import os
import falcon
from .storage.in_memory_storage import InMemoryStorage
from .pushbullet_api import PushbulletAPI
from .resources.users import UsersResource, UserResource, \
    UserNotificationsResource
from .resources.groups import GroupsResource, GroupResource, \
    GroupNotificationsResource
from .resources.notifications import NotificationsResource


def setup_api(storage=None, pushbullet=None):
    """Setup a WSGI API with the given storage and pushbullet api."""
    api = falcon.API()

    if not storage:
        storage = InMemoryStorage()
    if not pushbullet:
        pushbullet = PushbulletAPI(
            os.environ.get("PUSHBULLET_API_URL",
                           "https://api.pushbullet.com/v2"))

    api.add_route('/v1/users', UsersResource(storage))
    api.add_route('/v1/users/{username}', UserResource(storage))
    api.add_route('/v1/users/{username}/notifications',
                  UserNotificationsResource(storage, pushbullet))
    api.add_route('/v1/groups', GroupsResource(storage))
    api.add_route('/v1/groups/{group_id}', GroupResource(storage))
    api.add_route('/v1/groups/{group_id}/notifications',
                  GroupNotificationsResource(storage, pushbullet))

    api.add_route('/v1/notifications',
                  NotificationsResource(storage, pushbullet))

    return api


api = setup_api()
