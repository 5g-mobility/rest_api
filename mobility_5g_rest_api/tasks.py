# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(track_started=True)
def add(x, y):
    print(x + y)
    return


def sum(x,y):
    print(x+y)
