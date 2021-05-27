import math
import datetime
import time

import geopy.distance
from dash.dependencies import Output, Input
from django.core.management.base import BaseCommand
import xml.etree.cElementTree as ET
import paho.mqtt.client as mqtt
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import threading
import random

from mobility_5g_rest_api.models import RadarEvent


class Command(BaseCommand):
    help = 'Runs the MQTT Consumer'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.perceived_objects_on_zone = []
        self.checkpoint = (0, 0), (0, 0)
        self.sec_epoch_2004 = int((datetime.datetime(2004, 1, 1) - datetime.datetime(1970, 1, 1)).total_seconds())
        self.old_iteration = []
        self.to_delete = []
        self.map_objects = []
        self.map_time = datetime.datetime.now()

    def add_arguments(self, parser):
        parser.add_argument('--broker_url', nargs=1, type=str, required=True)
        parser.add_argument('--broker_port', nargs=1, type=int, required=True)
        parser.add_argument('--broker_user', nargs=1, type=str, required=False)
        parser.add_argument('--broker_pw', nargs=1, type=str, required=False)
        parser.add_argument('--client_id', nargs=1, type=str, required=True)
        parser.add_argument('--topic', nargs=1, type=str, required=True)
        parser.add_argument("--map", help="Show Map Helper", action='store_true')

    def generate_map(self):
        # Objects -> [(lat, lon, car_id)]
        mapbox_access_token = open(".mapbox_token").read()

        app = dash.Dash()
        app.layout = html.Div([
            dcc.Graph(id='map', style={'width': '100vw', 'height': '100vh'}),
            dcc.Interval(
                id='interval-component',
                interval=300,
                n_intervals=0
            )
        ])

        @app.callback(Output('map', 'figure'),
                      Input('interval-component', 'n_intervals'))
        def update_map(n):
            lats = [lat for lat, lon, car_id, speed in self.map_objects]
            lons = [lon for lat, lon, car_id, speed in self.map_objects]
            text_ids_speed = ["ID: {} Speed: {}".format(car_id, speed) for lat, lon, car_id, speed in self.map_objects]
            fig = go.Figure(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='markers+text',
                marker=go.scattermapbox.Marker(
                    size=9
                ),
                text=text_ids_speed,
                textposition="bottom right"
            ))

            fig.update_layout(
                title=str(self.map_time),
                autosize=True,
                hovermode='closest',
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    style="satellite",
                    bearing=0,
                    center=dict(
                        lat=40.607120,
                        lon=-8.748817
                    ),
                    pitch=0,
                    zoom=17
                ),
            )
            return fig

        app.run_server(debug=True, use_reloader=False)

    def handle(self, *args, **options):
        print("Starting MQTT Consumer")

        if options.get('map'):
            threading.Thread(target=self.generate_map, args=(), daemon=True).start()

        client = mqtt.Client(options.get("client_id")[0])
        if options.get("broker_user") and options.get("broker_pw"):
            client.username_pw_set(options.get("broker_user")[0], options.get("broker_pw")[0])
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.connect(options.get("broker_url")[0], options.get("broker_port")[0])

        radar_id = int(options.get("topic")[0][23:24])

        if radar_id == 7:
            self.checkpoint = (40, -9), (41, -8)
        elif radar_id == 8:
            pass
        elif radar_id == 9:
            pass
        else:
            print("Radar not supported!")
            quit()

        client.subscribe(options.get("topic")[0])
        client.on_message = self.on_message

        client.loop_forever()

    def on_message(self, client, userdata, message):
        print("\n New Message \n")
        sec_time_since_2004 = int((datetime.datetime.utcnow() - datetime.datetime(2004, 1, 1)).total_seconds() * 1000)
        multiplier = math.floor(sec_time_since_2004 / 65536)

        xml = ET.fromstring(str(message.payload.decode("utf-8")))

        station_id = int(xml.find('header').find('stationID').text)
        cpm = xml.find('cpm')
        timestamp_delta = int(cpm.find('generationDeltaTime').text)
        cpm_parameters = cpm.find('cpmParameters')
        management_container = cpm_parameters.find('managementContainer')
        reference_position = management_container.find('referencePosition')
        longitude = int(reference_position.find('longitude').text) / 10000000
        latitude = int(reference_position.find('latitude').text) / 10000000
        # print(station_id, timestamp_delta, longitude, latitude)

        sec_time_in_radar_since_2004 = (65536 * multiplier + timestamp_delta) / 1000

        time_in_radar_epoch = datetime.datetime.fromtimestamp(sec_time_in_radar_since_2004 + self.sec_epoch_2004,
                                                              tz=datetime.timezone.utc)
        # print(time_in_radar_epoch)

        time_in_radar_until_seconds = time_in_radar_epoch.replace(microsecond=0)

        perceived_objects_ids = []
        map_objects = []

        for obj in cpm_parameters.find('perceivedObjectContainer').findall('PerceivedObject'):

            object_id = int(obj.find('objectID').text)
            x_distance = int(obj.find('xDistance').find('value').text) / 100
            y_distance = int(obj.find('yDistance').find('value').text) / 100
            x_speed = int(obj.find('xSpeed').find('value').text) / 100
            y_speed = int(obj.find('ySpeed').find('value').text) / 100

            perceived_objects_ids.append(object_id)

            if object_id in self.perceived_objects_on_zone:
                pass  # -> Continue

            print("\n", object_id, x_distance, y_distance, x_speed, y_speed)

            speed = math.ceil(x_speed + y_speed * 3.6)

            angle_of_object = math.atan(x_distance / y_distance) + 180
            vector_distance_object = math.sqrt(x_distance ** 2 + y_distance ** 2) / 1000
            # vector = y_distance/math.cos(angle_of_object)
            object_position = geopy.distance.distance(kilometers=vector_distance_object) \
                .destination((latitude, longitude), bearing=angle_of_object)
            object_position = (object_position.latitude, object_position.longitude)

            map_objects.append((object_position[0], object_position[1], object_id, speed))

            if self.checkpoint[0][0] <= object_position[0] <= self.checkpoint[1][0] and self.checkpoint[0][1] <= \
                    object_position[1] <= self.checkpoint[1][1]:
                self.perceived_objects_on_zone.append(object_id)

            print(time_in_radar_epoch)
            print(speed, str(object_position[0]) + "," + str(object_position[1]))

            # Save object
            '''RadarEvent.objects.create(timestamp=time_in_radar_until_seconds,
                                      velocity=speed,
                                      latitude=object_position[0],
                                      longitude=object_position[1],
                                      radar_id=station_id
                                      )'''

        self.map_objects = map_objects
        self.map_time = time_in_radar_epoch

        old_objects_not_in_this_iteration = [obj_id for obj_id in self.old_iteration if
                                             obj_id not in perceived_objects_ids]
        for obj_id in self.to_delete:
            if obj_id not in old_objects_not_in_this_iteration:
                if obj_id in self.perceived_objects_on_zone:
                    self.perceived_objects_on_zone.remove(obj_id)
                    self.to_delete.remove(obj_id)

        for obj_id in old_objects_not_in_this_iteration:
            if obj_id not in self.to_delete:
                self.to_delete.append(obj_id)

        self.old_iteration = perceived_objects_ids

    def on_connect(self, client, userdata, flags, rc):
        self.stdout.write(self.style.SUCCESS("Connected With Result Code: {}".format(rc)))

    def on_disconnect(self, client, userdata, rc):
        self.stdout.write(self.style.ERROR("Client Got Disconnected"))
