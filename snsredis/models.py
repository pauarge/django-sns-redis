from boto import sns
from boto.exception import BotoClientError, BotoServerError
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django_redis import get_redis_connection

VALID_PLATFORMS = (
    ('apns', 'APNS'),
    ('gcm', 'GCM')
)


class SNSToken(models.Model):
    arn = models.CharField(max_length=128)
    registration_id = models.TextField()
    user = models.ForeignKey(User, db_index=True)
    platform = models.CharField(max_length=4, choices=VALID_PLATFORMS)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'snsredis'
        unique_together = ('arn', 'user')


class UserManager(object):
    def __init__(self, user):
        self.redis = get_redis_connection('default')
        region = sns.connect_to_region(settings.AWS_SES_REGION_NAME, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                       aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY).region
        self.conn = sns.SNSConnection(region=region, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        self.user = user

    def get_endpoints(self):
        return self.redis.smembers('sns-endpoints:{}'.format(self.user.id))

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
            try:
                ret = self.conn.create_platform_endpoint(platform_application_arn=app_arn, token=token)
                endpoint_arn = ret.get('CreatePlatformEndpointResponse').get('CreatePlatformEndpointResult').get(
                    'EndpointArn')
                SNSToken.objects.get_or_create(user=self.user, arn=endpoint_arn,
                                               defaults={'registration_id': token, 'platform': platform})
            except BotoClientError as e:
                # TODO: Handle client errors
                raise e
            except BotoServerError as e:
                # TODO: Handle server errors
                raise e

    def remove_token(self, token):
        if isinstance(token, str) or isinstance(token, unicode):
            obj = SNSToken.objects.filter(user=self.user, registration_id=token)
            if obj:
                for o in obj:
                    try:
                        self.conn.delete_endpoint(o.arn)
                        o.delete()
                    except BotoClientError as e:
                        # TODO: Handle client errors
                        raise e
                    except BotoServerError as e:
                        # TODO: Handle server errors
                        raise e


class TopicManager(object):
    def __init__(self):
        raise NotImplementedError
