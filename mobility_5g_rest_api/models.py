from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from djongo import models

# Create your models here.
class Event(models.Model):
    LOCATION = [
        ("CN", "Costa Nova"),   #carbon footprint
        ("BA", "Barra"),        #carbon footprint
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
        ("CF", "Carbon Footprint"),
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
        ("CS", "Car Speeding"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=2, choices=LOCATION)
    event_type = models.CharField(max_length=2, choices=EVENT_TYPE)
    event_class = models.CharField(max_length=2, choices=EVENT_CLASS, null=True)
    velocity = models.IntegerField(
        validators=[
            MaxValueValidator(300),
            MinValueValidator(-300)
        ]
    )
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90)], null=True
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180)], null=True
    )
    co2km = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return str(self.timestamp) + ", " + str(self.location) + ": " + str(self.event_type)

    def clean(self):
        if self.event_type != "CF" and not self.event_class:
            raise ValidationError(
                {'event_class': "Blank is only allowed when type is Carbon Footprint"})

        if (self.event_type != "CO" or self.event_type != "CF") and not self.latitude:
            raise ValidationError(
                {'latitude': "Latitude is only allowed when type is Carbon Footprint or Conditions"})

        if (self.event_type != "CO" or self.event_type != "CF") and not self.longitude:
            raise ValidationError(
                {'longitude': "Longitude is only allowed when type is Carbon Footprint or Conditions"})

        if self.event_type != "CF" and not self.co2km:
            raise ValidationError(
                {'co2km': "CO2km is only allowed when type is Carbon Footprint"})

        if (self.event_type != "CO" or self.event_type != "CF") and (self.location == "BA" or self.location == "CN"):
            raise ValidationError(
                {'location': "Location Barra and Costa Nova are only allowed for Condition or Carbon Footprint events"})

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

