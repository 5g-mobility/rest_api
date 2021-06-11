# Create your tasks here
from __future__ import absolute_import, unicode_literals
from mobility_5g_rest_api.models import Event, RadarEvent
import json
from datetime import datetime, timedelta
from celery import shared_task
from celery.utils.log import get_task_logger

from mobility_5g_rest_api.utils import process_daily_inflow

logger = get_task_logger(__name__)


@shared_task(track_started=True)
def sensor_fusion(json_data):
    # Do the sensor fusion
    json_obj = json.loads(json_data)
    print(json_obj)

    location = None

    if json_obj:
        timestamp_event = datetime.strptime(json_obj[0]['date'], "%Y-%m-%d %H:%M:%S")
        if json_obj[0]['radarId'] == 5:
            location = 'PT'
        elif json_obj[0]['radarId'] == 7:
            location = 'RA'

        vehicles_to_process = []
        for event in json_obj:
            if event['inside_road']:
                if event['class'] in ['car', 'truck', 'motocycle']:
                    vehicles_to_process.append(event)

                elif event['class'] == 'person':
                    Event.objects.create(location=location,
                                         event_type="RD",
                                         event_class="PE",
                                         timestamp=timestamp_event)

                elif event['class'] in ['cat', 'dog', 'horse', 'sheep', 'cow', 'bear']:
                    Event.objects.create(location=location,
                                         event_type="RD",
                                         event_class="AN",
                                         timestamp=timestamp_event)

            else:
                if event['class'] in ['cat', 'dog', 'horse', 'sheep', 'cow', 'bear']:
                    Event.objects.create(location=location,
                                         event_type="BL",
                                         event_class="AN",
                                         timestamp=timestamp_event)

                elif event['class'] == 'person':
                    Event.objects.create(location=location,
                                         event_type="BL",
                                         event_class="PE",
                                         timestamp=timestamp_event)

                elif event['class'] == 'bicycle':
                    Event.objects.create(location=location,
                                         event_type="BL",
                                         event_class="BC",
                                         timestamp=timestamp_event)

        if vehicles_to_process:
            neg_velocity_radar_events = list(RadarEvent.objects.filter(timestamp=timestamp_event,
                                                                       radar_id=json_obj[0]['radarId'],
                                                                       velocity__lt=0))
            pos_velocity_radar_events = list(RadarEvent.objects.filter(timestamp=timestamp_event,
                                                                       radar_id=json_obj[0]['radarId'],
                                                                       velocity__gt=0))
            last_5_seconds_radar_events_gt = list(RadarEvent.objects.filter(
                timestamp__gte=(timestamp_event - timedelta(seconds=5)),
                radar_id=json_obj[0]['radarId'], velocity__gt=0))
            last_5_seconds_radar_events_lt = list(RadarEvent.objects.filter(
                timestamp__gte=(timestamp_event - timedelta(seconds=5)),
                radar_id=json_obj[0]['radarId'], velocity__lt=0))

            for event in reversed(vehicles_to_process):
                if event['is_stopped']:
                    Event.objects.create(location=location,
                                         event_type="RD",
                                         event_class="SC",
                                         timestamp=timestamp_event)
                else:
                    radar_event = None
                    event_class = 'CA' if event['class'] == 'car' else ('TR' if event['class'] == 'truck' else 'MC')
                    if event['speed'] > 0:
                        if pos_velocity_radar_events:
                            radar_event = pos_velocity_radar_events[0]
                            Event.objects.create(location=location,
                                                 event_type="RT",
                                                 event_class=event_class,
                                                 timestamp=radar_event.timestamp,
                                                 velocity=abs(radar_event.velocity))
                            radar_event.delete()
                            pos_velocity_radar_events.remove(radar_event)
                        else:
                            if last_5_seconds_radar_events_gt:
                                radar_event = last_5_seconds_radar_events_gt[0]
                                Event.objects.create(location=location,
                                                     event_type="RT",
                                                     event_class=event_class,
                                                     timestamp=radar_event.timestamp,
                                                     velocity=abs(radar_event.velocity))
                                radar_event.delete()
                                last_5_seconds_radar_events_gt.remove(radar_event)

                    elif event['speed'] < 0:
                        if neg_velocity_radar_events:
                            radar_event = neg_velocity_radar_events[0]
                            Event.objects.create(location=location,
                                                 event_type="RT",
                                                 event_class=event_class,
                                                 timestamp=radar_event.timestamp,
                                                 velocity=abs(radar_event.velocity))
                            radar_event.delete()
                            neg_velocity_radar_events.remove(radar_event)
                        else:
                            if last_5_seconds_radar_events_lt:
                                radar_event = last_5_seconds_radar_events_lt[0]
                                Event.objects.create(location=location,
                                                     event_type="RT",
                                                     event_class=event_class,
                                                     timestamp=radar_event.timestamp,
                                                     velocity=abs(radar_event.velocity))
                                radar_event.delete()
                                last_5_seconds_radar_events_lt.remove(radar_event)

                    if radar_event:
                        process_daily_inflow(radar_event, location)

    return "Processed the JSON {}".format(json_data)
