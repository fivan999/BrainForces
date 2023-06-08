import redis

import django.conf


redis_connection = redis.Redis(
    host=django.conf.settings.REDIS_HOST,
    port=django.conf.settings.REDIS_PORT,
    db=django.conf.settings.REDIS_DB,
)
