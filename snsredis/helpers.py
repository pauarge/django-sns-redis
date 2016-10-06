from boto import sns
from django.conf import settings
from django_redis import get_redis_connection
import collections
import json


def format_message(message, extra=None, sound=None, badge=None, mutable_content=1):
    if not isinstance(extra, collections.Mapping):
        extra = {}

    aps = {
        'alert': message,
        'mutable-content': mutable_content
    }
    if sound:
        aps['sound'] = sound
    if badge:
        try:
            aps['badge'] = int(badge)
        except ValueError:
            pass
    apns = {
        "aps": aps,
    }
    apns.update(extra)

    gcm = {
        'message': message
    }
    gcm.update(extra)

    data = {
        "APNS": json.dumps(apns),
        "GCM": json.dumps({
            "data": gcm
        })
    }
    return json.dumps(data)


def get_connection_sns():
    region = sns.connect_to_region(settings.AWS_REGION_NAME, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY).region
    return sns.SNSConnection(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, region=region,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


def get_connection_redis():
    if settings.SNSREDIS_REDIS_CONNECTION:
        return get_redis_connection(settings.SNSREDIS_REDIS_CONNECTION)
    else:
        return get_redis_connection('default')
