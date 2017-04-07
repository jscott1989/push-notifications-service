"""Utilities related to Falcon requests and responses."""
import json
import codecs
import falcon


def decode_json_request(request, keys=[]):
    """Decode a json request.
    If any of the required keys are not included,
    a HTTPBadRequest exception will be raised."""
    data = {}
    if request.content_length:
        reader = codecs.getreader("utf-8")
        data = json.load(reader(request.stream))
    for key in keys:
        if key not in data:
            raise falcon.HTTPBadRequest("Missing required data '%s'" % key)
    return data
