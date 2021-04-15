from rest_framework import viewsets

from mobility_5g_rest_api.models import Event, Climate, DailyInflow
from mobility_5g_rest_api.serializers import EventSerializer, ClimateSerializer, DailyInflowSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class ClimateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Climate.objects.all()
    serializer_class = ClimateSerializer


class DailyInflowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyInflow.objects.all()
    serializer_class = DailyInflowSerializer
