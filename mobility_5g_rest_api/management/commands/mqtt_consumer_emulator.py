import time
from threading import Thread

from django.core.management.base import BaseCommand
import json
import paho.mqtt.client as mqtt
import datetime

from mobility_5g_rest_api.models import Event


class Command(BaseCommand):
    help = 'Runs the MQTT Consumer'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.last_vehicle_status = {}
        self.barra_lat_lon_boundaries = (40.64436, 40.63111), (-8.75093, -8.73451)
        self.costa_lat_lon_boundaries = (40.63119, 40.60714), (-8.75845, -8.74338)
        self.climate_status = {"BA": [], "CN": []}

    def add_arguments(self, parser):
        parser.add_argument('--broker_url', nargs=1, type=str, required=True)
        parser.add_argument('--broker_port', nargs=1, type=int, required=True)
        parser.add_argument('--client_id', nargs=1, type=str, required=True)
        parser.add_argument('--topic', nargs=1, type=str, required=True)

    def handle(self, *args, **options):
        print("Starting MQTT Consumer")

        client = mqtt.Client(options.get("client_id")[0])
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.connect(options.get("broker_url")[0], options.get("broker_port")[0])

        client.subscribe(options.get("topic")[0])
        client.on_message = self.on_message

        client.loop_forever()

    def on_message(self, client, userdata, message):
        print("\n CALMEX \n")
        json_msg = json.loads(str(message.payload.decode("utf-8")))

        vehicle_id = json_msg["vehicle_id"]
        timestamp = json_msg["tm"]
        latitude = json_msg["latitude"][0]
        longitude = json_msg["position"][1]
        co2_emissions = json_msg["co2_emissions"]
        speed = json_msg["speed"]
        air_temperature = json_msg["air_temperature"]
        light_sensor = json_msg["light_sensor"]
        rain_sensor = json_msg["rain_sensor"]
        fog_light_sensor = json_msg["fog_light_sensor"]

        if self.barra_lat_lon_boundaries[0][1] <= latitude <= self.barra_lat_lon_boundaries[0][0]:
            location = "BA"
        elif self.costa_lat_lon_boundaries[0][1] <= latitude <= self.costa_lat_lon_boundaries[0][0]:
            location = "CN"
        else:
            return

        if self.barra_lat_lon_boundaries[1][1] <= longitude <= self.barra_lat_lon_boundaries[1][0]:
            if location == "CN":
                return
        elif self.costa_lat_lon_boundaries[1][1] <= longitude <= self.costa_lat_lon_boundaries[1][0]:
            if location == "BA":
                return
        else:
            return

        if vehicle_id not in self.last_vehicle_status:
            self.last_vehicle_status[vehicle_id] = [air_temperature, light_sensor, rain_sensor, fog_light_sensor,
                                                    co2_emissions, datetime.datetime.now(), location, latitude,
                                                    longitude, speed]

            Event.objects.create(location=location,
                                 timestamp=timestamp,
                                 event_type="CO",
                                 event_class="OT",
                                 latitude=latitude,
                                 longitude=longitude,
                                 velocity=speed,
                                 temperature=air_temperature)

            if light_sensor:
                light_event_class = "LT"
            else:
                light_event_class = "NL"
            Event.objects.create(location=location,
                                 timestamp=timestamp,
                                 event_type="CO",
                                 event_class=light_event_class,
                                 latitude=latitude,
                                 longitude=longitude,
                                 velocity=speed)

            if rain_sensor:
                Event.objects.create(location=location,
                                     timestamp=timestamp,
                                     event_type="RA",
                                     event_class=light_event_class,
                                     latitude=latitude,
                                     longitude=longitude,
                                     velocity=speed)

            if fog_light_sensor:
                Event.objects.create(location=location,
                                     timestamp=timestamp,
                                     event_type="FO",
                                     event_class=light_event_class,
                                     latitude=latitude,
                                     longitude=longitude,
                                     velocity=speed)
        else:
            if abs(air_temperature - self.last_vehicle_status[vehicle_id][0]) > 1.75:
                self.last_vehicle_status[vehicle_id][0] = air_temperature
                Event.objects.create(location=location,
                                     timestamp=timestamp,
                                     event_type="CO",
                                     event_class="OT",
                                     latitude=latitude,
                                     longitude=longitude,
                                     velocity=speed,
                                     temperature=air_temperature)
                # Criar climate com nova temp com as info do ultimo climate
            if light_sensor != self.last_vehicle_status[vehicle_id][1]:
                if light_sensor:
                    light_event_class = "LT"
                else:
                    light_event_class = "NT"
                Event.objects.create(location=location,
                                     timestamp=timestamp,
                                     event_type="CO",
                                     event_class=light_event_class,
                                     latitude=latitude,
                                     longitude=longitude,
                                     velocity=speed)
            if rain_sensor != self.last_vehicle_status[vehicle_id][2]:
                if rain_sensor:
                    Event.objects.create(location=location,
                                         timestamp=timestamp,
                                         event_type="RA",
                                         event_class=light_event_class,
                                         latitude=latitude,
                                         longitude=longitude,
                                         velocity=speed)
            if fog_light_sensor != self.last_vehicle_status[vehicle_id][3]:
                if fog_light_sensor:
                    Event.objects.create(location=location,
                                         timestamp=timestamp,
                                         event_type="FO",
                                         event_class=light_event_class,
                                         latitude=latitude,
                                         longitude=longitude,
                                         velocity=speed)

        if co2_emissions:
            self.last_vehicle_status[vehicle_id][4] += co2_emissions

            if self.last_vehicle_status[vehicle_id][4] > 100:
                Event.objects.create(location=location,
                                     timestamp=timestamp,
                                     event_type="CO",
                                     event_class="CF",
                                     latitude=latitude,
                                     longitude=longitude,
                                     velocity=speed,
                                     co2=self.last_vehicle_status[vehicle_id][4])

        if speed > 90:
            Event.objects.create(location=location,
                                 timestamp=timestamp,
                                 latitude=latitude,
                                 longitude=longitude,
                                 event_type="CO",
                                 event_class="CS",
                                 velocity=speed)

        self.last_vehicle_status[vehicle_id][5] = datetime.datetime.now()
        self.last_vehicle_status[vehicle_id][6] = location
        self.last_vehicle_status[vehicle_id][7] = latitude
        self.last_vehicle_status[vehicle_id][8] = longitude
        self.last_vehicle_status[vehicle_id][9] = speed


    def on_connect(self, client, userdata, flags, rc):
        self.stdout.write(self.style.SUCCESS("Connected With Result Code: {}".format(rc)))
        t = Thread(target=self.update_co2, args=(), daemon=True)
        t.start()

    def update_co2(self):
        while True:
            time.sleep(60*12)
            for car in self.last_vehicle_status:
                actualTime = datetime.datetime.now()
                if (datetime.datetime.now() - self.last_vehicle_status[car][5]).total_seconds() > 100:
                    if self.last_vehicle_status[car][4] > 0:
                        Event.objects.create(location=self.last_vehicle_status[car][6],
                                             timestamp=actualTime,
                                             event_type="CO",
                                             event_class="CF",
                                             latitude=self.last_vehicle_status[car][7],
                                             longitude=self.last_vehicle_status[car][8],
                                             velocity=self.last_vehicle_status[car][9],
                                             co2=self.last_vehicle_status[car][4])

    def on_disconnect(self, client, userdata, rc):
        self.stdout.write(self.style.ERROR("Client Got Disconnected"))
