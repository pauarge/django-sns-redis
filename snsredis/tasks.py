from boto import sns

from django.conf import settings
from models import UserManager


def add_token(user_id, token, platform):
    manager = UserManager(user_id)
    manager.add_token(token, platform)


def publish(user_id, message=None, extra=None):
    manager = UserManager(user_id)
    apns, gcm = manager.get_endpoints()

    region = sns.connect_to_region(settings.AWS_SNS_REGION_NAME).region
    conn = sns.SNSConnection(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, region=region,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    if len(apns) > 0:
        apns_message = ''
        for e in apns:
            conn.publish(target_arn=e, message=apns_message, message_structure='json')

    if len(gcm) > 0:
        gcm_message = ''
        for e in gcm:
            conn.publish(target_arn=e, message=gcm_message, message_structure='json')
