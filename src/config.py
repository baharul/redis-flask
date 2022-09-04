import os


class Config(object):
    CACHE_TYPE='redis'
    CACHE_REDIS_HOST='jp-redis-d01.j1cmo9.ng.0001.aps1.cache.amazonaws.com:6379'
    CACHE_REDIS_PORT=6379
    CACHE_REDIS_DB=0
    CACHE_REDIS_URL='redis://jp-redis-d01.j1cmo9.ng.0001.aps1.cache.amazonaws.com:6379/0'
    CACHE_DEFAULT_TIMEOUT=500