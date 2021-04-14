from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from mobility_5g_rest_api.models import Event, Climate, DailyInflow
from mobility_5g_rest_api.serializers import EventSerializer, ClimateSerializer, DailyInflowSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EventSerializer


class ClimateViewSet(viewsets.ModelViewSet):
    queryset = Climate.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ClimateSerializer


class DailyInflowViewSet(viewsets.ModelViewSet):
    queryset = DailyInflow.objects.all()
    permission_classes = [AllowAny]
    serializer_class = DailyInflowSerializer
