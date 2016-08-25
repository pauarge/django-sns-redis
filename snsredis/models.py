from boto import sns

VALID_PLATFORMS = ['apns', 'gcm']


class UserManager(object):
    def __init__(self, redis, user_id=None):
        self.redis = redis
        self.user_id = user_id

    # Returns a dict with "apns" and "gcm" as keys.
    # Each key contains all endpoints associated with self.user_id
    def get_endpoints(self):
        raise NotImplementedError

    def get_user(self):
        return self.user_id

    def set_user(self, user_id):
        self.user_id = user_id

    def add_token(self, token, platform=None):
        # TODO: Token check
        if platform in VALID_PLATFORMS:
            # Boto request
            # save return to redis
            pass


class TopicManager(object):
    def __init__(self, redis=None):
        raise NotImplementedError
