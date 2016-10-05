from boto.exception import BotoServerError
from django.conf import settings
from django.contrib.auth.models import User

from .helpers import format_message, get_connection_sns, get_connection_redis
from .models import SNSToken, UserManager


def add_token(user, token, platform):
    manager = UserManager(user)
    manager.add_token(token, platform)


def remove_token(user, token):
    manager = UserManager(user)
    manager.remove_token(token)


def prune_tokens(platform):
    if platform == 'apns':
        app_arn = settings.AWS_SNS_APNS_ARN
    elif platform == 'gcm':
        app_arn = settings.AWS_SNS_GCM_ARN
    else:
        return
    conn = get_connection_sns()
    res = conn.list_endpoints_by_platform_application(platform_application_arn=app_arn)
    while res.get('ListEndpointsByPlatformApplicationResponse').get('ListEndpointsByPlatformApplicationResult').get(
            'NextToken'):
        endpoints = res.get('ListEndpointsByPlatformApplicationResponse').get(
            'ListEndpointsByPlatformApplicationResult').get('Endpoints')
        for ep in endpoints:
            endpoint_arn = ep.get('EndpointArn')
            token = ep.get('Attributes').get('Token')
            if ep.get('Attributes').get('Enabled') == 'true':
                objs = SNSToken.objects.filter(registration_id=token).exclude(arn=endpoint_arn)
                for o in objs:
                    conn.delete_endpoint(o.arn)
                    o.delete()
            else:
                conn.delete_endpoint(endpoint_arn)
                SNSToken.objects.filter(arn=endpoint_arn).delete()
        res = conn.list_endpoints_by_platform_application(platform_application_arn=app_arn, next_token=res.get(
            'ListEndpointsByPlatformApplicationResponse').get('ListEndpointsByPlatformApplicationResult').get(
            'NextToken'))


def prune_user_tokens(user):
    tokens = SNSToken.objects.filter(user=user)
    if len(tokens) > 1:
        conn = get_connection_sns()
        registred_ids = []
        for t in tokens:
            attr = conn.get_endpoint_attributes(t.arn).get('GetEndpointAttributesResponse').get(
                'GetEndpointAttributesResult').get('Attributes')
            if attr.get('Enabled') == 'true':
                if attr.get('Token') in registred_ids:
                    conn.delete_endpoint(t.arn)
                    t.delete()
                else:
                    registred_ids.append(attr.get('Token'))
            else:
                conn.delete_endpoint(t.arn)
                t.delete()


def rebuild_redis():
    redis = get_connection_redis()
    users = User.objects.all()
    for user in users:
        _hash = 'sns-endpoints:{}'.format(user.id)
        tokens = SNSToken.objects.filter(user=user)
        redis.delete(_hash)
        for t in tokens:
            redis.lpush(_hash, t.arn)


def publish(user, message=None, extra=None, sound=None, badge=None, mutable_content=1):
    manager = UserManager(user)
    endpoints = manager.get_endpoints()

    if len(endpoints) > 0:
        formatted_message = format_message(message, extra, sound, badge, mutable_content)
        conn = get_connection_sns()

        for ep in endpoints:
            try:
                conn.publish(target_arn=ep, message=formatted_message, message_structure='json')
            except BotoServerError as e:
                obj = SNSToken.objects.filter(user=user, arn=ep)
                if e.error_code == 'EndpointDisabled':
                    obj.delete()
                    conn.delete_endpoint(ep)
                elif e.error_code == 'InvalidParameter':
                    obj.delete()
                else:
                    raise e
