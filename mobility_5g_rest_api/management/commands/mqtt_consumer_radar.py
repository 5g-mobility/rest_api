import math
import datetime

import geopy.distance
from django.core.management.base import BaseCommand, CommandError
import json
import paho.mqtt.client as mqtt


class Command(BaseCommand):
    help = 'Runs the MQTT Consumer'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.old_perceived_objects = {}
        self.popped = []
        self.checkpoint = (41.2400078, -8.6950224)
        self.sec_epoch_2004 = int((datetime.datetime(2004, 1, 1) - datetime.datetime(1970, 1, 1)).total_seconds())

    def add_arguments(self, parser):
        parser.add_argument('--broker_url', nargs=1, type=str, required=True)
        parser.add_argument('--broker_port', nargs=1, type=int, required=True)
        parser.add_argument('--broker_user', nargs=1, type=str, required=False)
        parser.add_argument('--broker_pw', nargs=1, type=str, required=False)
        parser.add_argument('--client_id', nargs=1, type=str, required=True)
        parser.add_argument('--topic', nargs=1, type=str, required=True)

    def handle(self, *args, **options):
        print("Starting MQTT Consumer")

        client = mqtt.Client(options.get("client_id")[0])
        if options.get("broker_user") and options.get("broker_pw"):
            client.username_pw_set(options.get("broker_user")[0], options.get("broker_pw")[0])
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.connect(options.get("broker_url")[0], options.get("broker_port")[0])

        client.subscribe(options.get("topic")[0])
        client.on_message = self.on_message

        client.loop_forever()

    def on_message(self, client, userdata, message):
        #print("\n New Message \n")
        sec_time_since_2004 = int((datetime.datetime.utcnow() - datetime.datetime(2004, 1, 1)).total_seconds() * 1000)
        multiplier = math.floor(sec_time_since_2004 / 65536)

        json_msg = json.loads(str(message.payload.decode("utf-8")))


        station_id = json_msg["station_id"]
        timestamp_delta = json_msg["timestamp_delta"]
        longitude = json_msg["longitude"] / 10000000
        latitude = json_msg["latitude"] / 10000000
        #print(station_id, timestamp_delta, longitude, latitude)

        sec_time_in_radar_since_2004 = (65536 * multiplier + timestamp_delta) / 1000

        time_in_radar_epoch = datetime.datetime.fromtimestamp(sec_time_in_radar_since_2004 + self.sec_epoch_2004,
                                                              tz=datetime.timezone.utc)
        #print(time_in_radar_epoch)

        perceived_objects = json_msg["perceived_objects"]

        object_ids_this_iteration = []

        for obj in perceived_objects:
            object_id = obj["objectID"]
            x_distance = obj["xDistance"] / 100
            y_distance = obj["yDistance"] / 100
            x_speed = obj["xSpeed"] / 100
            y_speed = obj["ySpeed"] / 100

            if x_distance > 10 or y_distance > 45:
                continue

            if object_id in self.popped:
                print("Object deleted is reappearing!!")
                print(object_id)
                quit()

            print("\n", object_id, x_distance, y_distance, x_speed, y_speed)

            object_ids_this_iteration.append(object_id)

            speed = math.ceil(x_speed + y_speed * 3.6)

            angle_of_object = math.atan(x_distance / y_distance)
            vector_distance_object = math.sqrt(x_distance * 2 + y_distance ** 2) / 1000
            object_position = geopy.distance.distance(kilometers=vector_distance_object) \
                .destination((latitude, longitude), bearing=angle_of_object)
            object_position = (object_position.latitude-4.163380242516723e-05, object_position.longitude+-2.1216887722275146e-05)
            print(time_in_radar_epoch)
            print(speed, str(object_position[0])+","+str(object_position[1]))

            if object_id not in self.old_perceived_objects:
                self.old_perceived_objects[object_id] = ([time_in_radar_epoch], [speed], [object_position])
            else:
                self.old_perceived_objects[object_id][0].append(time_in_radar_epoch)
                self.old_perceived_objects[object_id][1].append(speed)
                self.old_perceived_objects[object_id][2].append(object_position)

        for obj_id_to_db in [obj_id for obj_id in self.old_perceived_objects if
                             obj_id not in object_ids_this_iteration]:
            print(obj_id_to_db)
            self.popped.append(obj_id_to_db)

            speed_list = self.old_perceived_objects[obj_id_to_db][1]
            average_speed = math.ceil(sum(speed_list) / len(speed_list))

            latitude_list = [position[0] for position in self.old_perceived_objects[obj_id_to_db][2]]
            average_latitude = sum(latitude_list) / len(latitude_list)

            longitude_list = [position[1] for position in self.old_perceived_objects[obj_id_to_db][2]]
            average_longitude = sum(longitude_list) / len(longitude_list)

            distances_to_checkpoint = [
                geopy.distance.distance(position, self.checkpoint).km
                for position in self.old_perceived_objects[obj_id_to_db][2]]
            timestamp_pos = distances_to_checkpoint.index(min(distances_to_checkpoint))

            timestamp = self.old_perceived_objects[obj_id_to_db][0][timestamp_pos]

            print(average_speed, average_latitude, average_longitude, timestamp)
            self.old_perceived_objects.pop(obj_id_to_db)

    def on_connect(self, client, userdata, flags, rc):
        self.stdout.write(self.style.SUCCESS("Connected With Result Code: {}".format(rc)))

    def on_disconnect(self, client, userdata, rc):
        self.stdout.write(self.style.ERROR("Client Got Disconnected"))
