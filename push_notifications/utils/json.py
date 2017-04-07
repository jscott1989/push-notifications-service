"""JSON utilities."""

import json
from datetime import datetime


def _json_serial(obj):
    """Serialize unknown objects to JSON."""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def json_dump(obj):
    """Dump JSON to text.
    This applies additional serializing functions over json.dumps."""
    return json.dumps(obj, default=_json_serial)
