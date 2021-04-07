from django.core.validators import MaxValueValidator, MinValueValidator
from djongo import models

# Create your models here.
class Event(models.Model):
    #TODO Validor outros tipos vs Carbon
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
        ("NL", "No lights"),
        ("CS", "Car Speeding"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=2, choices=LOCATION)
    event_type = models.CharField(max_length=2, choices=EVENT_TYPE)
    event_class = models.CharField(max_length=2, choices=EVENT_CLASS, blank=True)
    velocity = models.IntegerField(
        validators=[
            MaxValueValidator(300),
            MinValueValidator(-300)
        ], blank=True
    )
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90)], blank=True
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180)], blank=True
    )
    co2km = models.DecimalField(max_digits=5, decimal_places=2, blank=True)

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