import time
from random import uniform

import paho.mqtt.client as mqtt

mqttBroker = "mqtt.eclipseprojects.io"

client = mqtt.Client("Temperature_Inside")
client.connect(mqttBroker)

while True:
    randNumber = uniform(20.0, 21.0)
    client.publish("BARRA", randNumber)
    print("Just published " + str(randNumber) + " to topic TEMPERATURE")
    time.sleep(1)
