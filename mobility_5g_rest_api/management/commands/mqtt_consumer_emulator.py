from django.core.management.base import BaseCommand
import json
import paho.mqtt.client as mqtt

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

        location = None

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
            self.last_vehicle_status[vehicle_id] = [air_temperature, light_sensor, rain_sensor, fog_light_sensor]
        else:
            if air_temperature != self.last_vehicle_status[vehicle_id][0]:
                pass
            if light_sensor != self.last_vehicle_status[vehicle_id][1]:
                pass
            if rain_sensor != self.last_vehicle_status[vehicle_id][2]:
                pass
            if fog_light_sensor != self.last_vehicle_status[vehicle_id][3]:
                pass

        if co2_emissions > 0:
            Event.objects.create(location=location,
                                 timestamp=timestamp,
                                 event_type="CO",
                                 event_class="CF",
                                 latitude=latitude,
                                 longitude=longitude,
                                 co2=co2_emissions)

        if speed > 90:
            Event.objects.create(location=location,
                                 timestamp=timestamp,
                                 latitude=latitude,
                                 longitude=longitude,
                                 event_type="CO",
                                 event_class="CS",
                                 velocity=speed)

    def on_connect(self, client, userdata, flags, rc):
        self.stdout.write(self.style.SUCCESS("Connected With Result Code: {}".format(rc)))

    def on_disconnect(self, client, userdata, rc):
        self.stdout.write(self.style.ERROR("Client Got Disconnected"))
