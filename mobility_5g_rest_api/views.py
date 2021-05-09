from rest_framework import viewsets

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
