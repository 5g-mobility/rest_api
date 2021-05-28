from django.core.management.base import BaseCommand, CommandError
from mobility_5g_rest_api.models import Event
import paho.mqtt.client as mqtt


class Command(BaseCommand):
    help = 'Example of a MQTT Consumer'

    def add_arguments(self, parser):
        parser.add_argument('--broker_url', nargs='?', type=str)
        parser.add_argument('--broker_port', nargs='?', type=int)
        parser.add_argument('--client_id', nargs='?', type=str)
        parser.add_argument('--topic', nargs='?', type=str)

    def handle(self, *args, **options):
        print("Starting MQTT Consumer")
        client = mqtt.Client(options.get("client_id") or "5g-mobility-consumer")
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.connect(options.get("broker_url") or "mqtt.eclipseprojects.io", options.get("broker_port") or 1883)

        client.subscribe(options.get("topic") or "BARRA")
        client.on_message = self.on_message

        client.loop_forever()

    def on_message(self, client, userdata, message):
        self.stdout.write(self.style.SUCCESS("received message: {}".format(str(message.payload.decode("utf-8")))))
        self.stdout.write(self.style.SUCCESS("message topic={}".format(message.topic)))
        self.stdout.write(self.style.SUCCESS("message qos={}".format(message.qos)))
        self.stdout.write(self.style.SUCCESS("message retain flag=".format(message.retain)))

        Event.objects.create(location="DN",
                             event_type="RT",
                             event_class="CA",
                             velocity=250)

    def on_connect(self, client, userdata, flags, rc):
        self.stdout.write(self.style.SUCCESS("Connected With Result Code: {}".format(rc)))

    def on_disconnect(self, client, userdata, rc):
        self.stdout.write(self.style.ERROR("Client Got Disconnected"))
