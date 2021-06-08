# Create your tasks here
from __future__ import absolute_import, unicode_literals
from mobility_5g_rest_api.models import Event, RadarEvent
import json
from datetime import datetime, timedelta
from celery import shared_task
from celery.utils.log import get_task_logger

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
            print(reversed(vehicles_to_process))
            neg_velocity_radar_events = RadarEvent.objects.filter(timestamp=timestamp_event,
                                                                  radar_id=json_obj[0]['radarId'],
                                                                  velocity__lt=0)
            pos_velocity_radar_events = RadarEvent.objects.filter(timestamp=timestamp_event,
                                                                  radar_id=json_obj[0]['radarId'],
                                                                  velocity__gt=0)

            for event in reversed(vehicles_to_process):
                if event['is_stopped']:
                    Event.objects.create(location=location,
                                         event_type="RD",
                                         event_class="SC",
                                         timestamp=timestamp_event)
                else:
                    event_class = 'CA' if event['class'] == 'car' else ('TR' if event['class'] == 'truck' else 'MC')
                    if event['speed'] > 0:
                        if pos_velocity_radar_events:
                            radar_event = pos_velocity_radar_events[0]
                            Event.objects.create(location=location,
                                                 event_type="RT",
                                                 event_class=event_class,
                                                 timestamp=timestamp_event,
                                                 velocity=radar_event.velocity)
                            radar_event.delete()
                        else:
                            last_5_seconds_radar_events = RadarEvent.objects.filter(
                                timestamp__gte=(timestamp_event - timedelta(seconds=5)),
                                radar_id=json_obj[0]['radarId'], velocity__gt=0)

                            if last_5_seconds_radar_events:
                                radar_event = last_5_seconds_radar_events[0]
                                Event.objects.create(location=location,
                                                     event_type="RT",
                                                     event_class=event_class,
                                                     timestamp=timestamp_event,
                                                     velocity=radar_event.velocity)
                                radar_event.delete()



                    elif event['speed'] < 0:
                        if pos_velocity_radar_events:
                            radar_event = neg_velocity_radar_events[0]
                            Event.objects.create(location=location,
                                                 event_type="RT",
                                                 event_class=event_class,
                                                 timestamp=timestamp_event,
                                                 velocity=radar_event.velocity)
                            radar_event.delete()
                        else:
                            last_5_seconds_radar_events = RadarEvent.objects.filter(
                                timestamp__gte=(timestamp_event - timedelta(seconds=5)),
                                radar_id=json_obj[0]['radarId'], velocity__lt=0)
                            if last_5_seconds_radar_events:
                                radar_event = last_5_seconds_radar_events[0]
                                Event.objects.create(location=location,
                                                     event_type="RT",
                                                     event_class=event_class,
                                                     timestamp=timestamp_event,
                                                     velocity=radar_event.velocity)
                                radar_event.delete()

        radar_events = RadarEvent.objects.filter(timestamp=timestamp_event, radar_id=json_obj[0]['radarId'])
        for event in radar_events:
            Event.objects.create(location=location,
                                 event_type="RT",
                                 event_class="CA",
                                 timestamp=timestamp_event,
                                 velocity=event.velocity)
            event.delete()

        old_radar_events = RadarEvent.objects.filter(timestamp__lt=(timestamp_event-timedelta(seconds=5)), radar_id=json_obj[0]['radarId'])
        for event in old_radar_events:
            Event.objects.create(location=location,
                                 event_type="RT",
                                 event_class="CA",
                                 timestamp=event.timestamp,
                                 velocity=event.velocity)
            event.delete()

    return "Processed the JSON {}".format(json_data)
