from django.test import TestCase

from models import SNSToken


class SNSRedisTestCase(TestCase):
    def setUp(self):
        pass

    def register_device(self):
        self.assertEqual(True, True)

    def send_notification(self):
        self.assertEqual(True, True)

    def unregister_device(self):
        self.assertEqual(True, True)
