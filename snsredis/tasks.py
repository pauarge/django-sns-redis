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


def prune_user_tokens(user):
    tokens = SNSToken.objects.filter(user=user)
    if len(tokens) > 1:
        conn = get_connection_sns()
        registred_ids = []
        for t in tokens:
            attr = conn.get_endpoint_attributes(t.arn).get('GetEndpointAttributesResponse').get('GetEndpointAttributesResult').get('Attributes')
            if attr.get('Enabled') == 'true':
                if attr.get('Token') in registred_ids:
                    print("FOUND DUPLICATED")
                    conn.delete_endpoint(t.arn)
                    t.delete()
                else:
                    print("FOUND NEW")
                    registred_ids.append(attr.get('Token'))
            else:
                print("FOUND DISABLED")
                conn.delete_endpoint(t.arn)
                t.delete()


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
