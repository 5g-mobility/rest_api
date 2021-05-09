from rest_framework import serializers

from mobility_5g_rest_api.models import Event, Climate, DailyInflow


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('timestamp', 'location', 'event_type', 'event_class', 'velocity', 'latitude', 'longitude', 'co2',
                  'temperature')


class ClimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Climate
        fields = ('timestamp', 'location', 'condition', 'daytime', 'temperature')


class DailyInflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyInflow
        fields = ('date', 'location', 'maximum', 'current')
