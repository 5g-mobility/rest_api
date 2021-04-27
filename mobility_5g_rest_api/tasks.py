# Create your tasks here
from __future__ import absolute_import, unicode_literals
from mobility_5g_rest_api.models import Event
from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@shared_task()
def add(x, y):
    return x + y

@shared_task()
def print_json(json):
    print(json)
    return json

@shared_task(track_started=True)
def sensor_fusion(json):
    # Do the sensor fusion
    print(json)

    ev = Event.objects.create(location="DN",
                              event_type="RT",
                              event_class="CA",
                              velocity=250)


    # return "Celery has imported {0} tweets from Twitter.".format(n)
    return "{} created {}".format(json, ev)
