from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .helpers import get_connection_redis
from .models import SNSToken


@receiver(post_save, sender=SNSToken)
def add_token_to_redis(sender, instance=None, created=False, **kwargs):
    if created:
        redis = get_connection_redis()
        hash_arn = 'sns-endpoints:{}'.format(instance.user_id)
        redis.lpush(hash_arn, instance.arn)


@receiver(post_delete, sender=SNSToken)
def remove_token_from_redis(sender, instance=None, **kwargs):
    redis = get_connection_redis()
    redis.lrem('sns-endpoints:{}'.format(instance.user_id), 0, instance.arn)
