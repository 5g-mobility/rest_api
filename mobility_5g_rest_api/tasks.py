# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task()
def add(x, y):
    return x + y


@shared_task()
def mul(x, y):
    return x * y


@shared_task()
def xsum(numbers):
    return sum(numbers)

'''
@shared_task(bind=True, track_started=True)
def c_get_tweets(self, uid, tweet_ids):
    """An asynchronous function to get tweets via Tweepy wrapper for Twitter API.

    :param self: instance of the class used to update the status
    :type self: @shared_task
    :param uid: user ID
    :type uid: int
    :param tweet_ids: tweet IDs to be scraped via Twitter API
    :type tweet_ids: list
    """
    api = twitter_api()
    n = len(tweet_ids)

    for i, tweet_id in enumerate(tweet_ids):
        self.update_state(state='PROGRESS', meta={'done': i, 'total': n, 'uid': uid})

        tweet, created = Tweet.objects.get_or_create(tweet_id=tweet_id)
        get_tweets(api, tweet_id, tweet)

    return "Celery has imported {0} tweets from Twitter.".format(n)
'''