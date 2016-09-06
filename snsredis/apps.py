from django.apps import AppConfig


class SNSRedisConfig(AppConfig):
    name = 'snsredis'

    def ready(self):
        from snsredis import signals