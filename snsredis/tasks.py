from boto.exception import BotoClientError, BotoServerError
from django.conf import settings

from helpers import format_message, get_connection_sns
from models import SNSToken, UserManager


def add_token(user, token, platform):
    manager = UserManager(user)
    manager.add_token(token, platform)


def remove_token(user, token):
    manager = UserManager(user)
    manager.remove_token(token)


def publish(user, message=None, extra=None, sound=None, badge=None):
    manager = UserManager(user)
    endpoints = manager.get_endpoints()

    if len(endpoints) > 0:
        formatted_message = format_message(message, extra, sound, badge)
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
