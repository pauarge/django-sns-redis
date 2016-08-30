from boto import sns
from django.settings import conf
from django_redis import get_redis_connection
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
            "aps": apns
        }),
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
    if conf.SNSREDIS_REDIS_CONNECTION:
        return get_redis_connection(conf.SNSREDIS_REDIS_CONNECTION)
    else:
        return get_redis_connection('default')
