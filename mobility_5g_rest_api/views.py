import datetime

from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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
        data["CO2"] = sum(
            Event.objects.filter(location="BA", event_type="CO", event_class="CF").values_list('co2', flat=True))
    elif location == "CN":
        data["CO2"] = sum(
            Event.objects.filter(location="CN", event_type="CO", event_class="CF").values_list('co2', flat=True))
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
            max_speed_this_day = max(day_events.values_list('velocity', flat=True))
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

    location = request.query_params.get('location', None)

    if location not in ["RA", "DN", "PT"]:
        data['error'] = "Location must be RA, DN or PT"
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    for x in range(30):
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dategte = today - datetime.timedelta(days=x)
        datelt = dategte + datetime.timedelta(days=1)

        day_events = Event.objects.filter(location=location, timestamp__lt=datelt, timestamp__gte=dategte, event_type="RT")

        number_this_day = day_events.count()
        if number_this_day > 0:
            max_speed_this_day = max(day_events.values_list('velocity', flat=True))
        else:
            max_speed_this_day = 0

        data[dategte.strftime("%d/%m/%y")] = max_speed_this_day

    return Response(data, status=st)

@api_view(['GET'])
@permission_classes([AllowAny])
def max_daily_inflow_summary(request):
    data = {}
    st = status.HTTP_200_OK

    for location in ['CN', 'BA']:
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
