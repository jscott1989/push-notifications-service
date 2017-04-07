"""A simple Notification Server."""

import falcon
from .storage.in_memory_storage import InMemoryStorage
from .resources.users import UsersResource, UserResource


def setup_api(storage=None):
    """Setup a WSGI API with the given storage."""
    api = falcon.API()

    if not storage:
        storage = InMemoryStorage()

    api.add_route('/v1/users', UsersResource(storage))
    api.add_route('/v1/users/{username}', UserResource(storage))

    return api


api = setup_api()
