import math
import datetime
import time

from geopy import distance
from dash.dependencies import Output, Input
from django.core.management.base import BaseCommand
import xml.etree.cElementTree as ET
import paho.mqtt.client as mqtt
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import threading

from mobility_5g_rest_api.models import RadarEvent


class Command(BaseCommand):
    help = 'Runs the MQTT Radar Consumer'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.offset_lat_lon = (0, 0)
        self.perceived_objects_on_zone = []
        self.checkpoint = (0, 0), (0, 0)
        self.sec_epoch_2004 = int((datetime.datetime(2004, 1, 1) - datetime.datetime(1970, 1, 1)).total_seconds())
        self.last_time = datetime.datetime(1970, 1, 1)
        self.old_iteration = []
        self.to_delete = []
        self.to_delete_timestamp = []
        self.map_objects = []
        self.map_time = datetime.datetime.now()
        self.radar_id = None
        self.r_earth = 6371000.0
        self.map_lat_lon = (0, 0)
        self.offset_time = datetime.timedelta(seconds=0, milliseconds=0)

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

        fig = go.Figure(go.Scattermapbox(
            lat=[lat for lat, lon, car_id, speed in self.map_objects],
            lon=[lon for lat, lon, car_id, speed in self.map_objects],
            mode='markers+text',
            marker=go.scattermapbox.Marker(
                size=9
            ),
            text=["ID: {} Speed: {}".format(car_id, speed) for lat, lon, car_id, speed in self.map_objects],
            textposition="bottom right",
            textfont=dict(color='white', size=18)
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
                    lat=self.map_lat_lon[0],
                    lon=self.map_lat_lon[1]
                ),
                pitch=0,
                zoom=17
            ),
        )

        app = dash.Dash()
        app.layout = html.Div([
            dcc.Graph(id='map', style={'width': '100vw', 'height': '100vh'}, figure=fig),
            dcc.Interval(
                id='interval-component',
                interval=100,
                n_intervals=0
            )
        ])

        @app.callback(Output('map', 'figure'),
                      Input('interval-component', 'n_intervals'),
                      dash.dependencies.State('map', 'figure'))
        def update_map(n, fig):
            lats = [lat for lat, lon, car_id, speed in self.map_objects]
            lons = [lon for lat, lon, car_id, speed in self.map_objects]
            text_ids_speed = ["ID: {} Speed: {}".format(car_id, speed) for lat, lon, car_id, speed in self.map_objects]
            fig['data'][0]['lat'] = lats
            fig['data'][0]['lon'] = lons
            fig['data'][0]['text'] = text_ids_speed
            fig['layout']['title']['text'] = str(self.map_time)

            return fig

        app.run_server(debug=True, use_reloader=False)

    def handle(self, *args, **options):
        print("Starting MQTT Consumer")

        time.sleep(30)

        self.radar_id = int(options.get("topic")[0][23:24])

        if self.radar_id == 7:  # Ria Ativa
            self.checkpoint = (40.607300, -8.748921), (40.607173, -8.748802)
            self.map_lat_lon = (40.607120, -8.748817)
            self.offset_time = datetime.timedelta(seconds=12, milliseconds=000)
        elif self.radar_id == 5:  # Ponte Barra
            self.checkpoint = (40.628067, -8.732920)
            self.map_lat_lon = (40.627790, -8.732017)
            self.offset_lat_lon = (-0.000040, 0)
            self.offset_time = datetime.timedelta(seconds=10, milliseconds=500)
        else:
            print("Radar not supported!")
            quit()

        if options.get('map'):
            threading.Thread(target=self.generate_map, args=(), daemon=True).start()

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
        # print("\n New Message \n")
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

        ms_time_in_radar_since_2004 = (65536 * multiplier + timestamp_delta) / 1000

        time_in_radar_epoch = datetime.datetime.fromtimestamp(ms_time_in_radar_since_2004 + self.sec_epoch_2004) - \
                              self.offset_time

        if time_in_radar_epoch < self.last_time:
            return
        else:
            self.last_time = time_in_radar_epoch

        perceived_objects_ids = []
        map_objects = []

        for obj in cpm_parameters.find('perceivedObjectContainer').findall('PerceivedObject'):

            object_id = int(obj.find('objectID').text)
            x_distance = int(obj.find('xDistance').find('value').text) / 100
            y_distance = int(obj.find('yDistance').find('value').text) / 100
            x_speed = int(obj.find('xSpeed').find('value').text) / 100
            y_speed = int(obj.find('ySpeed').find('value').text) / 100

            perceived_objects_ids.append(object_id)

            # map_objects.append((self.checkpoint[0][0], self.checkpoint[0][1], 8178372183, 22))
            # map_objects.append((self.checkpoint[1][0], self.checkpoint[1][1], 8178372183, 22))

            if object_id in self.perceived_objects_on_zone:
                continue

            # print("\n", object_id, x_distance, y_distance, x_speed, y_speed)

            speed = math.ceil(math.sqrt(x_speed ** 2 + y_speed ** 2) * 3.6) * (1 if x_speed + y_speed > 0 else -1)

            new_latitude = (latitude + (y_distance / self.r_earth) * (180 / math.pi))
            new_longitude = (longitude + (x_distance / self.r_earth) * (180 / math.pi) / math.cos(new_latitude *
                                                                                                  math.pi / 180))
            object_position = new_latitude + self.offset_lat_lon[0], new_longitude + self.offset_lat_lon[1]

            map_objects.append((object_position[0], object_position[1], object_id, speed))

            if (self.radar_id == 7 and self.checkpoint[1][0] <= object_position[0] <= self.checkpoint[0][0] and
                self.checkpoint[0][1] <= \
                object_position[1] <= self.checkpoint[1][1]) or (
                    self.radar_id == 5 and distance.distance(self.checkpoint, object_position).km <= 0.050):
                self.perceived_objects_on_zone.append(object_id)

                # Save object
                if speed != 0:

                    time_in_radar_epoch_to_use = time_in_radar_epoch

                    if station_id == 5:
                        if speed > 0:
                            time_in_radar_epoch_to_use -= datetime.timedelta(seconds=1, milliseconds=150)
                        else:
                            time_in_radar_epoch_to_use += datetime.timedelta(seconds=1)

                    time_in_radar_until_seconds = time_in_radar_epoch_to_use.replace(microsecond=0)

                    # print("\n", time_in_radar_until_seconds)
                    # print(time_in_radar_epoch_to_use)
                    # print(speed, str(object_position[0]) + "," + str(object_position[1]), object_id, "\n")

                    RadarEvent.objects.create(timestamp=time_in_radar_until_seconds,
                                              velocity=speed,
                                              latitude=object_position[0],
                                              longitude=object_position[1],
                                              radar_id=station_id
                                              )
        self.map_objects = map_objects
        self.map_time = time_in_radar_epoch

        old_objects_not_in_this_iteration = [obj_id for obj_id in self.old_iteration if
                                             obj_id not in perceived_objects_ids]
        for index, obj_id in enumerate(self.to_delete):
            if obj_id not in old_objects_not_in_this_iteration:
                if obj_id in self.perceived_objects_on_zone:
                    if (time_in_radar_epoch-self.to_delete_timestamp[index]).total_seconds() > 45:
                        self.perceived_objects_on_zone.remove(obj_id)
                        self.to_delete.pop(index)
                        self.to_delete_timestamp.pop(index)

        for obj_id in old_objects_not_in_this_iteration:
            if obj_id not in self.to_delete:
                self.to_delete.append(obj_id)
                self.to_delete_timestamp.append(time_in_radar_epoch)

        self.old_iteration = perceived_objects_ids

    def on_connect(self, client, userdata, flags, rc):
        self.stdout.write(self.style.SUCCESS("Connected With Result Code: {}".format(rc)))

    def on_disconnect(self, client, userdata, rc):
        self.stdout.write(self.style.ERROR("Client Got Disconnected"))
        quit()
