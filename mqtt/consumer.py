import os
import paho.mqtt.client as mqtt
import django
import sys

# ATTENTION Implementation not used, only here for reference. We are using custom django-admin commands instead.

sys.path.append('../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api.settings")

django.setup()
from mobility_5g_rest_api.models import Event

broker_url = "mqtt.eclipseprojects.io"
broker_port = 1883


def on_message(client, userdata, message):
    print("received message: ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    ev = Event.objects.create(location="DN",
                              event_type="RT",
                              event_class="CA",
                              velocity=250)


def on_connect(client, userdata, flags, rc):
    print("Connected With Result Code: {}".format(rc))


def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected")


client = mqtt.Client("Smartphone")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect(broker_url, broker_port)


client.subscribe("HUGO_111")
client.on_message = on_message

client.loop_forever()