import collections
import json


def format_message(message, extra=None, sound=None):
    if not isinstance(extra, collections.Mapping):
        extra = {}

    apns = extra
    if sound:
        apns['sound'] = sound
    apns['alert'] = message

    gcm = extra
    gcm['message'] = message

    data = {
        "APNS": json.dumps({
            "aps": extra
        }),
        "GCM": json.dumps({
            "data": extra
        })
    }
    return json.dumps(data)
