import time
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from mobility_5g_rest_api.models import Event, RadarEvent
from mobility_5g_rest_api.utils import process_daily_inflow


class Command(BaseCommand):
    help = 'Processor of old radar events'

    def handle(self, *args, **options):
        print("Running Old Radar Event")
        while True:
            time.sleep(45)
            for radar_id in [5, 7]:
                if radar_id == 5:
                    location = 'PT'
                elif radar_id == 7:
                    location = 'RA'

                old_radar_events = RadarEvent.objects.filter(timestamp__lt=(datetime.now() - timedelta(seconds=45)),
                                                             radar_id=radar_id)
                for event in old_radar_events:
                    if abs(event.velocity) >= 5:
                        Event.objects.create(location=location,
                                             event_type="RT",
                                             event_class="CA",
                                             timestamp=event.timestamp,
                                             velocity=abs(event.velocity))

                        process_daily_inflow(event, location)

                    event.delete()
