import datetime

from django.db.models import Avg, Max, Sum
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import random

from mobility_5g_rest_api.models import Event, Climate, DailyInflow
from mobility_5g_rest_api.serializers import EventSerializer, ClimateSerializer, DailyInflowSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = {
        'timestamp': ['exact', 'lte', 'gte'],
        'location': ['exact'],
        'event_type': ['exact'],
        'event_class': ['exact', 'in'],
        'velocity': ['exact', 'lte', 'gte'],
        'latitude': ['exact', 'lte', 'gte'],
        'longitude': ['exact', 'lte', 'gte'],
        'co2': ['exact', 'lte', 'gte'],
        'temperature': ['exact', 'lte', 'gte'],
    }


class ClimateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Climate.objects.all()
    serializer_class = ClimateSerializer
    filterset_fields = {
        'location': ['exact'],
        'condition': ['exact'],
        'timestamp': ['exact', 'lte', 'gte'],
        'daytime': ['exact'],
        'temperature': ['exact', 'lte', 'gte'],
    }


class DailyInflowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyInflow.objects.all()
    serializer_class = DailyInflowSerializer
    filterset_fields = {
        'location': ['exact'],
        'maximum': ['exact', 'lte', 'gte'],
        'current': ['exact', 'lte', 'gte'],
        'date': ['exact', 'lte', 'gte'],
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def conditions_stats(request):
    data = {}
    st = status.HTTP_200_OK

    location = request.query_params.get('location', None)

    if location == "BA":
        data["FG"] = Climate.objects.filter(location="BA", condition="FG").count()
        data["CL"] = Climate.objects.filter(location="BA", condition="CL").count()
        data["RN"] = Climate.objects.filter(location="BA", condition="RN").count()
    elif location == "CN":
        data["FG"] = Climate.objects.filter(location="CN", condition="FG").count()
        data["CL"] = Climate.objects.filter(location="CN", condition="CL").count()
        data["RN"] = Climate.objects.filter(location="CN", condition="RN").count()
    else:
        st = status.HTTP_400_BAD_REQUEST
        data['error'] = "Location must be BA, or CN"

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def carbon_footprint(request):
    data = {}
    st = status.HTTP_200_OK

    location = request.query_params.get('location', None)

    if location == "BA":
        query_set = Event.objects.filter(location="BA", event_type="CO", event_class="CF")
        if query_set.count() > 0:
            data["CO2"] = query_set.aggregate(Sum('co2'))['co2__sum']
        else:
            data["CO2"] = 0
    elif location == "CN":
        query_set = Event.objects.filter(location="CN", event_type="CO", event_class="CF")
        if query_set.count() > 0:
            data["CO2"] = query_set.aggregate(Sum('co2'))['co2__sum']
        else:
            data["CO2"] = 0
    else:
        st = status.HTTP_400_BAD_REQUEST
        data['error'] = "Location must be BA, or CN"

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def daily_excessive_speed(request):
    data = {}
    st = status.HTTP_200_OK

    for x in range(30):
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dategte = today - datetime.timedelta(days=x)
        datelt = dategte + datetime.timedelta(days=1)

        day_events = Event.objects.filter(timestamp__lt=datelt, timestamp__gte=dategte, event_type="CO",
                                          event_class="CS")

        number_this_day = day_events.count()
        if number_this_day > 0:
            max_speed_this_day = day_events.aggregate(Max('velocity'))['velocity__max']
        else:
            max_speed_this_day = 0

        data[dategte.strftime("%d/%m/%y")] = {'number': number_this_day, 'top': max_speed_this_day}

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def circulation_vehicles(request):
    data = {}
    st = status.HTTP_200_OK

    location = request.query_params.get('location', None)
    dategte = request.query_params.get('timestamp__gte', None)
    datelte = request.query_params.get('timestamp__lte', datetime.datetime.now())

    try:
        data['cars'] = Event.objects.filter(location=location, event_type="RT", event_class="CA",
                                            timestamp__gte=dategte,
                                            timestamp__lte=datelte).count()
        data['trucks'] = Event.objects.filter(location=location, event_type="RT", event_class="TR",
                                              timestamp__gte=dategte,
                                              timestamp__lte=datelte).count()
        data['motorcycles'] = Event.objects.filter(location=location, event_type="RT", event_class="MC",
                                                   timestamp__gte=dategte,
                                                   timestamp__lte=datelte).count()
    except:
        data['error'] = "Location must be RA, DN or PT and timestamp__gte is needed"
        st = status.HTTP_400_BAD_REQUEST

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def top_speed_road_traffic_summary(request):
    data = {}
    st = status.HTTP_200_OK

    for location in ["RA", "PT"]:  # Add DN to include Duna data later on
        data[location] = {}
        for x in range(30):
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            dategte = today - datetime.timedelta(days=x)
            datelt = dategte + datetime.timedelta(days=1)

            day_events = Event.objects.filter(location=location, timestamp__lt=datelt, timestamp__gte=dategte,
                                              event_type="RT")

            number_this_day = day_events.count()
            if number_this_day > 0:
                max_speed_this_day = day_events.aggregate(Max('velocity'))['velocity__max']
            else:
                max_speed_this_day = 0

            data[location][dategte.strftime("%d/%m/%y")] = max_speed_this_day

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def max_daily_inflow_summary(request):
    data = {}
    st = status.HTTP_200_OK

    for location in ['BT']:  # Add CN and BA to include both zones later on
        data[location] = {}
        for x in range(30):
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date = today - datetime.timedelta(days=x)

            try:
                day_daily_inflow = DailyInflow.objects.get(location=location, date=date)
                data[location][date.strftime("%d/%m/%y")] = day_daily_inflow.maximum
            except DailyInflow.DoesNotExist:
                data[location][date.strftime("%d/%m/%y")] = 0

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def bike_lanes_stats(request):
    data = {}
    st = status.HTTP_200_OK

    location = request.query_params.get('location', None)
    dategte = request.query_params.get('timestamp__gte', None)
    datelte = request.query_params.get('timestamp__lte', datetime.datetime.now())

    try:
        data['people'] = Event.objects.filter(location=location, event_type="RT", event_class="PE",
                                              timestamp__gte=dategte,
                                              timestamp__lte=datelte).count()
        data['animals'] = Event.objects.filter(location=location, event_type="RT", event_class="BC",
                                               timestamp__gte=dategte,
                                               timestamp__lte=datelte).count()
        data['bikes'] = Event.objects.filter(location=location, event_type="RT", event_class="AN",
                                             timestamp__gte=dategte,
                                             timestamp__lte=datelte).count()
    except:
        data['error'] = "Location must be RA, DN or PT and timestamp__gte is needed"
        st = status.HTTP_400_BAD_REQUEST

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def current_traffic_stats(request):
    data = {}
    st = status.HTTP_200_OK

    now = datetime.datetime.now()
    thirty_sec_ago = now - datetime.timedelta(seconds=30)

    for location in ["RA", "PT"]:  # Add DN to include Duna data later on
        data[location] = {}
        objects = Event.objects.filter(location=location, timestamp__lte=now, timestamp__gte=thirty_sec_ago,
                                       event_type="RT")
        n_objects = objects.count()
        if n_objects > 0:
            avg_speed = objects.aggregate(Avg('velocity'))
            if avg_speed <= 30:
                data[location]['traffic'] = 'Slow'
            elif avg_speed > 90:
                data[location]['traffic'] = 'Excessive Speed'
            else:
                data[location]['traffic'] = 'Flowing Normally'
        else:
            data[location]['traffic'] = 'Flowing Normally'

        n_people = Event.objects.filter(location=location, timestamp__lte=now, timestamp__gte=thirty_sec_ago,
                                        event_class="PE").count()
        data[location]['people'] = n_people

    return Response(data, status=st)


@api_view(['GET'])
@permission_classes([AllowAny])
def random_events_overview(request):
    data = {}
    st = status.HTTP_200_OK

    now = datetime.datetime.now()
    one_day_ago = now - datetime.timedelta(days=1)

    option = random.randint(0, 2)

    if option == 0:
        data['text'] = 'Cars Speeding'
        data['value'] = Event.objects.filter(timestamp__lte=now, timestamp__gte=one_day_ago, event_type="RT",
                                             velocity__gt=90).count()
    elif option == 1:
        data['text'] = 'Max Speed'
        max_speed = Event.objects.filter(timestamp__lte=now, timestamp__gte=one_day_ago, event_type="RT") \
            .aggregate(Max('velocity'))['velocity__max']
        data['value'] = "{} km/h".format(max_speed) if max_speed else "0 km/h"
    elif option == 2:
        data['text'] = 'Road Danger Events'
        data['value'] = Event.objects.filter(timestamp__lte=now, timestamp__gte=one_day_ago, event_type="RD",
                                             velocity__gt=90).count()

    return Response(data, status=st)
