from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .helpers import get_connection_sns, get_connection_redis

VALID_PLATFORMS = (
    ('apns', 'APNS'),
    ('gcm', 'GCM')
)


@python_2_unicode_compatible
class SNSToken(models.Model):
    arn = models.CharField(max_length=128)
    registration_id = models.TextField()
    user = models.ForeignKey(User, db_index=True)
    platform = models.CharField(max_length=4, choices=VALID_PLATFORMS)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return '{} - {}'.format(self.user, self.platform)
        except UnicodeDecodeError:
            pass

    class Meta:
        app_label = 'snsredis'
        unique_together = ('arn', 'user')


class UserManager(object):
    def __init__(self, user):
        self.redis = get_connection_redis()
        self.conn = get_connection_sns()
        self.user = user

    def get_endpoints(self):
        return self.redis.lrange('sns-endpoints:{}'.format(self.user.id), 0, -1)

    def get_user(self):
        return self.user

    def set_user(self, user):
        self.user = user

    def add_token(self, token, platform):
        if isinstance(token, str) or isinstance(token, unicode):
            if platform == 'apns':
                app_arn = settings.AWS_SNS_APNS_ARN
            elif platform == 'gcm':
                app_arn = settings.AWS_SNS_GCM_ARN
            else:
                return
            ret = self.conn.create_platform_endpoint(platform_application_arn=app_arn, token=token)
            endpoint_arn = ret.get('CreatePlatformEndpointResponse').get('CreatePlatformEndpointResult').get(
                'EndpointArn')
            SNSToken.objects.get_or_create(user=self.user, arn=endpoint_arn,
                                           defaults={'registration_id': token, 'platform': platform})

    def remove_token(self, token):
        if isinstance(token, str) or isinstance(token, unicode):
            obj = SNSToken.objects.filter(user=self.user, registration_id=token)
            if obj:
                for o in obj:
                    self.conn.delete_endpoint(o.arn)
                    o.delete()


class TopicManager(object):
    def __init__(self):
        raise NotImplementedError
