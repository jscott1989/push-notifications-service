"""API for Pushbullet service."""
import requests
import json


class InvalidAccessTokenException(Exception):
    """The access token used is not valid."""
    pass


class PushbulletException(Exception):
    """An unknown pushbullet exception has occured.
    Details are included in the message."""
    pass


class PushbulletAPI:
    """An interface to the PushBullet service."""
    def __init__(self, api_url):
        self._api_url = api_url

    def _post(self, access_token, path, data):
        """Perform a POST request to the API.
        The path should follow the api_url passed to the constructor.
        """
        json_data = json.dumps(data)
        response = requests.post(
            "%s%s" % (self._api_url, path), json_data, headers={
                "Access-Token": access_token,
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 401:
            # Invalid token. There will be a specific message in the JSON
            error_message = response.json()["error"]["message"]
            raise InvalidAccessTokenException(error_message)
        elif not response.status_code == 200:
            # 200 is the only valid response according to API docs.
            # (they must not use others in the 200-300 range)
            error_message = response.json()["error"]["message"]
            raise PushbulletException(error_message)

        return response

    def create_push(self, access_token, title, body):
        """Create a new push."""
        self._post(access_token, "/pushes", {
            "title": title,
            "body": body,
            "type": "note"
        })
