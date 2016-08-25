from boto import sns
from django.conf import settings
from django_redis import get_redis_connection

VALID_PLATFORMS = ['apns', 'gcm']


class UserManager(object):
    def __init__(self, user_id=None):
        self.redis = get_redis_connection('default')
        region = sns.connect_to_region(settings.AWS_SNS_REGION_NAME).region
        self.conn = sns.SNSConnection(region=region, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        self.user_id = user_id

    # Returns two dicts with apns and gcm endpoints.
    def get_endpoints(self):
        _hash_apns = 'sns-endpoint:{}:apns'.format(self.user_id)
        _hash_gcm = 'sns-endpoint:{}:gcm'.format(self.user_id)
        return self.redis.smembers(_hash_apns), self.redis.smembers(_hash_gcm)

    def get_user(self):
        return self.user_id

    def set_user(self, user_id):
        self.user_id = user_id

    def add_token(self, token, platform=None):
        # TODO: Token check
        if platform in VALID_PLATFORMS:
            if platform == 'apns':
                arn = settings.AWS_SNS_APNS_ARN
                _hash = 'sns-endpoint:{}:apns'.format(self.user_id)
            else:
                arn = settings.AWS_SNS_GCM_ARN
                _hash = 'sns-endpoint:{}:gcm'.format(self.user_id)
            ret = self.conn.create_platform_endpoint(platform_application_arn=arn, token=token)
            arn = ret.get('CreatePlatformEndpointResponse').get('CreatePlatformEndpointResult').get('EndpointArn')
            self.redis.sadd(_hash, arn)


class TopicManager(object):
    def __init__(self):
        raise NotImplementedError
