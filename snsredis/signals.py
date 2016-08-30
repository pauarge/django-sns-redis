from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django_redis import get_redis_connection

from models import SNSToken


@receiver(post_save, sender=SNSToken)
def add_token_to_redis(sender, instance=None, created=False, **kwargs):
    if created:
        redis = get_redis_connection()
        hash_arn = 'sns-endpoints:{}'.format(instance.user_id)
        redis.lpush(hash_arn, instance.arn)


@receiver(post_delete, sender=SNSToken)
def remove_token_from_redis(sender, instance=None, **kwargs):
    redis = get_redis_connection()
    redis.lrem('sns-endpoints:{}'.format(instance.user_id), instance.arn)
