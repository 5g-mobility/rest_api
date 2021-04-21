# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

from mobility_5g_rest_api.models import Event

logger = get_task_logger(__name__)


@shared_task(track_started=True)
def sensor_fusion(json):
    # Do the sensor fusion
    print(json)

    ev = Event.objects.create(location="DN",
                              event_type="RT",
                              event_class="CA",
                              velocity=250)

    return "{} created {}".format(json, ev)
