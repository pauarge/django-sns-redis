from builtins import input
from django.test import TestCase
from django.contrib.auth.models import User

from .models import SNSToken
from .helpers import get_connection_redis, get_connection_sns
from .tasks import add_token, publish, remove_token


class SNSRedisTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="test_user")

    def register_device(self):
        redis = get_connection_redis()
        self.assertEqual(True, True)

    def send_notification(self):
        self.assertEqual(True, True)

    def unregister_device(self):
        self.assertEqual(True, True)
