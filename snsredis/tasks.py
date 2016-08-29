from boto import sns
from boto.exception import BotoClientError, BotoServerError
from django.conf import settings

from models import SNSToken, UserManager
import format


def add_token(user, token, platform):
    manager = UserManager(user)
    manager.add_token(token, platform)


def remove_token(user, token):
    manager = UserManager(user)
    manager.remove_token(token)


def publish(user, message=None, extra=None, sound=None):
    manager = UserManager(user)
    endpoints = manager.get_endpoints()

    region = sns.connect_to_region(settings.AWS_SNS_REGION_NAME).region
    conn = sns.SNSConnection(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, region=region,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    if len(endpoints) > 0:
        formatted_message = format.format_message(message, extra, sound)
        for ep in endpoints:
            try:
                conn.publish(target_arn=ep, message=formatted_message, message_structure='json')
            except BotoClientError as e:
                # TODO: Handle client errors
                raise e
            except BotoServerError as e:
                if e.error_code == 'EndpointDisabled':
                    obj = SNSToken.objects.filter(user=user, arn=e)
                    obj.delete()
                else:
                    raise e
