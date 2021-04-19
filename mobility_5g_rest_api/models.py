from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from djongo import models


class Event(models.Model):
    LOCATION = [
        ("CN", "Costa Nova"),
        ("BA", "Barra"),
        ("RA", "Ria Ativa"),
        ("DN", "Duna"),
        ("PT", "Ponte Barra"),
        ("25", "A25 Aveiro"),
    ]

    EVENT_TYPE = [
        ("RT", "Road Traffic"),
        ("RD", "Road Danger"),
        ("BL", "Bike Lanes"),
        ("CO", "Conditions"),
    ]

    EVENT_CLASS = [
        ("AN", "Animal"),
        ("PE", "Person"),
        ("SO", "Strange Object"),
        ("SC", "Stopped Car"),
        ("CA", "Car"),
        ("BC", "Bicycle"),
        ("MC", "Motorcycle"),
        ("TR", "Truck"),
        ("RA", "Rain"),
        ("FO", "Fog"),
        ("NL", "No light"),
        ("LT", "Light"),
        ("OT", "Outside Temperature"),
        ("CS", "Car Speeding"),
        ("CF", "Carbon Footprint")
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=2, choices=LOCATION)
    event_type = models.CharField(max_length=2, choices=EVENT_TYPE)
    event_class = models.CharField(
        max_length=2, choices=EVENT_CLASS)
    velocity = models.IntegerField(
        validators=[
            MaxValueValidator(400),
            MinValueValidator(-400)
        ]
    )
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90)], blank=True
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180)], blank=True
    )
    co2km = models.FloatField(blank=True, validators=[MinValueValidator(0.0)])
    temperature = models.FloatField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return str(self.timestamp) + ", " + str(self.location) + ": " + str(self.event_type) + ": " + str(
            self.event_class)

    def clean(self):
        if (self.location == "RA" or self.location == "DN" or self.location == "PT" or self.location == "25") \
                and self.event_type == "CO":
            raise ValidationError(
                {'location': 'Location Ria Ativa, Duna, Ponte da Barra and A25 are not allowed for Conditions events'}
            )

        if (self.event_class == "RA" or self.event_class == "FO" or self.event_class == "NL"
            or self.event_class == "LT" or self.event_class == "OT" or self.event_class == "CS" or self.event_class == "CF") and self.event_type != "CO":
            raise ValidationError(
                {'event_type': 'Event_class Rain, Fog, No Light, Light, Outside Temperature, Car Speeding and Carbon '
                               'Footprint are only allowed for the Conditions event type'}
            )

        if (self.event_class == "AN" or self.event_class == "PE") and (
                self.event_type != "BL" or self.event_type != "RD"):
            raise ValidationError(
                {'event_type': 'Event_class Animal and Person are only allowed for the Bike Lanes or Road Danger '
                               'event type'}
            )

        if self.event_class == "BC" and (self.event_type != "BL" or self.event_type != "RT"):
            raise ValidationError(
                {'event_type': 'Event_class Bicycle is only allowed for the Bike Lanes or Road Traffic event type'}
            )

        if (
                self.event_class == "CA" or self.event_class == "MC" or self.event_class == "TR") and self.event_type != "RT":
            raise ValidationError(
                {'event_type': 'Event_class Car, Motorcycle and Truck are only allowed for the '
                               'Road Traffics event type'}
            )

        if self.event_type != "CO" and self.latitude:
            raise ValidationError(
                {'latitude': "Latitude is only allowed when event type is Conditions"})

        if self.event_type != "CO" and self.longitude:
            raise ValidationError(
                {'longitude': "Longitude is only allowed when event type Conditions"})

        if (self.event_type != "CO" or (self.event_type == "CO" and self.event_class != "CF")) and self.co2km:
            raise ValidationError(
                {'co2km': "CO2km is only allowed when type is Conditions and class is Carbon Footprint"})

        if self.event_type == "CO" and not self.latitude:
            raise ValidationError(
                {'latitude': "Latitude needs to have value"})

        if self.event_type == "CO" and not self.longitude:
            raise ValidationError(
                {'longitude': "Longitude needs to have value"})

        if self.event_type == "CO" and self.event_class == "CF" and not self.co2km:
            raise ValidationError(
                {'co2km': "CO2km needs to have value"})

        if self.event_type == "CO" and self.event_class == "OT" and not self.temperature:
            raise ValidationError(
                {'temperature': "Temperature needs to have value"})

        if (self.event_type != "CO" or self.event_class != "OT") and self.temperature:
            raise ValidationError(
                {'temperature': "Temperature is only allowed when type is Conditions and class Outside Temperature"})

        if self.event_type != "CO" and (self.location == "BA" or self.location == "CN"):
            raise ValidationError(
                {'location': "Location Barra and Costa Nova are only allowed for Conditions events"})

        if (self.event_class == "SO" or self.event_class == "SC") and self.event_type != "RD":
            raise ValidationError(
                {'event_type': 'Event_class Strange Objects or Stopped Car are only allowed for'
                               'event_type Road Danger'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Climate(models.Model):
    LOCATION = [
        ("CN", "Costa Nova"),
        ("BA", "Barra")
    ]
    CONDITION = [
        ("FG", "Fog"),
        ("CL", "Clean"),
        ("RN", "Rain"),
    ]

    location = models.CharField(max_length=2, choices=LOCATION)
    condition = models.CharField(max_length=2, choices=CONDITION)
    timestamp = models.DateTimeField(auto_now_add=True)
    daytime = models.BooleanField()  # True - Day, False - Night
    temperature = models.FloatField()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return str(self.timestamp) + ", " + str(self.condition) + ": " + str(self.daytime) + ": " + str(
            self.temperature)


class DailyInflow(models.Model):
    LOCATION = [
        ("CN", "Costa Nova"),
        ("BA", "Barra")
    ]

    location = models.CharField(max_length=2, choices=LOCATION)
    maximum = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    current = models.IntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    date = models.DateField(auto_now_add=True)
    temperature = models.FloatField()
    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(self.date) + ", " + str(self.maximum) + ": " + str(self.current)

    def clean(self):
        if self.maximum < self.current:
            raise ValidationError(
                {'maximum': 'Maximum value needs to be higher or equals to current'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

# Event
# - ID
# - Timestamp
# - Location (Ponte, Ria...) ou (Costa Nova/Barra) para carbonfootprint
# - Type (Road_Traffic, Road_danger, Bike_Lanes, Conditions, Carbon_Footprint)
# - Class
#     - Animal, Person, Strange_Objects, Stopped_car - > Road_danger_event
#     - Cars, bikes, moto, camião -> Road_Traffic_Event
#     - Bike (Animal & Person) -> Bike_Lanes_Event
#     - Rain, fog, no_light, car_speeding -> Conditions_Event
# - Velocity
# - GeoLocation (só para conditions e carbonfooprint)
# - co2/km (só para carbonfootprint)
