"""General notification functions."""
from push_notifications.storage import UserNotFoundException
from push_notifications.pushbullet_api import InvalidAccessTokenException, \
    PushbulletException


def send_notification_to_user(pushbullet_api, storage, logger,
                              user, title, body):
    """Send a notification to a user.
    Returns if True, None if there is no error.
    otherwise False, followed by the error."""
    try:
        access_token = storage.get_by_username(user)
        pushbullet_api.create_push(access_token, title, body)
        storage.increment_notifications_pushed(user)
        logger.info("Notification pushed to %s" % user)
        return True, None
    except UserNotFoundException:
        logger.error("User not found %s" % user)
        return False, "%s: User not found" % user
    except InvalidAccessTokenException:
        logger.error("Invalid pushbullet access token %s" % access_token)
        return False, "%s: Incorrect access token" % user
    except PushbulletException as e:
        logger.error("Pushbullet error %s" % str(e))
        return False, "%s: Pushbullet error" % user
