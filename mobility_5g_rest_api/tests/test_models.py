from django.core.exceptions import ValidationError
from django.test import TestCase
from datetime import datetime
from datetime import date


from faker import Faker

from mobility_5g_rest_api.models import Event, Climate, DailyInflow, RadarEvent

fake = Faker()


class EventTest(TestCase):
    def test_event_creation(self):
        location = "DN"
        event_type = "RT"
        event_class = "CA"
        velocity = fake.random_int(-300, 300)
        ev = Event.objects.create(
            timestamp=datetime.now(),
            location=location,
            event_type=event_type,
            event_class=event_class,
            velocity=velocity
        )
        self.assertEquals(ev.location, location, "Location not equal!")
        self.assertEquals(ev.event_type, event_type, "Event Type not equal!")
        self.assertEquals(ev.event_class, event_class,
                          "Event Class not equal!")
        self.assertEquals(ev.velocity, velocity, "Velocity not equal!")

    def test_cn_ba_location(self):
        with self.assertRaises(ValidationError, msg={'location': 'Location Barra and Costa Nova are only allowed for '
                                                                 'Conditions events'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="CN",
                event_type="RT",
                velocity=fake.random_int(-300, 300)
            )

    def test_event_class_conditions(self):
        with self.assertRaises(ValidationError, msg={
            'event_type': 'Event_class Rain, Fog, No Light, Light, Outside Temperature, Car Speeding and Carbon '
                          'Footprint are only allowed for the Conditions event type'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="RA",
                event_type="RT",
                event_class="CS",
                velocity=fake.random_int(-300, 300)
            )

    def test_cf_co_not_allowed_locations(self):
        with self.assertRaises(ValidationError, msg={'location': 'Location Ria Ativa, Duna, Ponte da Barra and A25 '
                                                                 'are not allowed for Conditions events'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="RA",
                event_type="CO",
                event_class="LT",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                longitude=fake.pydecimal(3, 2, False, -180, 180),
                velocity=fake.random_int(-300, 300)
            )

    def test_an_pe_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_type': 'Event_class Animal and Person are only allowed for the Bike Lanes '
                                                 'or Road Danger event type'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="RA",
                event_type="RT",
                event_class="AN",
                velocity=fake.random_int(-300, 300)
            )

    def test_bc_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_type': 'Event_class Bicycle is only allowed for the Bike Lanes or Road '
                                                 'Traffic event type'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="DN",
                event_type="RD",
                event_class="BC",
                velocity=fake.random_int(-300, 300)
            )

    def test_ca_mc_tr_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_type': 'Event_class Car, Motorcycle and Truck are only allowed for the Road '
                                                 'Traffics event type'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="PT",
                event_type="RD",
                event_class="CA",
                velocity=fake.random_int(-300, 300)
            )

    def test_latitude_longitude_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'latitude': 'Latitude is only allowed when event type is Conditions'}) and self.assertRaises(
            ValidationError,
            msg={
                'longitude': 'Longitude is only allowed when event type is Conditions'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="PT",
                event_type="RT",
                event_class="CA",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                velocity=fake.random_int(-300, 300)
            )

    def test_co2_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'co2': 'CO2 is only allowed when type is Conditions and class is Carbon '
                                            'Footprint'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="PT",
                event_type="CO",
                event_class="FO",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                longitude=fake.pydecimal(3, 2, False, -180, 180),
                co2=fake.pydecimal(3, 2, True),
                velocity=fake.random_int(-300, 300)
            )

    def test_co2_not_given(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'co2': 'CO2 needs to have value'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="PT",
                event_type="CO",
                event_class="CF",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                longitude=fake.pydecimal(3, 2, False, -180, 180),
                velocity=fake.random_int(-300, 300)
            )

    def test_temperature_no_value(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'temperature': 'Temperature needs to have value'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="BA",
                event_type="CO",
                event_class="OT",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                longitude=fake.pydecimal(3, 2, False, -180, 180),
                velocity=fake.random_int(-300, 300)
            )

    def test_temperature_not_allowed_event_class(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'temperature': 'Temperature is only allowed when type is Conditions and class '
                                                  'Outside Temperature'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="BA",
                event_type="CO",
                event_class="FO",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                longitude=fake.pydecimal(3, 2, False, -180, 180),
                temperature=fake.pydecimal(2, 2, False, -20, 40),
                velocity=fake.random_int(-300, 300)
            )

    def test_so_sc_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_type': 'Event_class Strange Objects or Stopped Car are only allowed for '
                                                 'event_type Road Danger'}):
            Event.objects.create(
                timestamp=datetime.now(),
                location="PT",
                event_type="RT",
                event_class="SO",
                velocity=fake.random_int(-300, 300)
            )


class ClimateTest(TestCase):
    def test_climate_creation(self):
        condition = "FG"
        location = "BA"
        daytime = fake.pybool()
        temperature = fake.pydecimal(2, 2, False)
        cl = Climate.objects.create(
            timestamp=datetime.now(),
            condition=condition,
            daytime=daytime,
            temperature=temperature,
            location=location
        )
        self.assertEquals(cl.condition, condition, "Condition not equal!")
        self.assertEquals(cl.daytime, daytime, "Daytime not equal!")
        self.assertEquals(cl.temperature, temperature,
                          "Temperature not equal!")
        self.assertEquals(cl.location, location, "Location not equal!")


class DailyInflowTest(TestCase):
    def test_daily_inflow_creation(self):
        location = "BA"
        maximum = fake.random_int(100, 300)
        current = fake.random_int(0, 99)
        dl = DailyInflow.objects.create(
            date=date.today().isoformat(),
            maximum=maximum,
            current=current,
            location=location
        )
        self.assertEquals(dl.maximum, maximum, "Maximum not equal!")
        self.assertEquals(dl.current, current, "Current not equal!")
        self.assertEquals(dl.location, location, "Location not equal!")

    def test_daily_inflow_maximum_less_than_current(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'maximum': 'Maximum value needs to be higher or equals to current'}):
            DailyInflow.objects.create(
                date=date.today().isoformat(),
                maximum=2,
                current=100,
            )


class RadarEventTest(TestCase):
    def test_event_creation(self):
        velocity = fake.pydecimal(2, 2, False, -400, 400)
        latitude = fake.pydecimal(2, 2, False, -90, 90)
        longitude = fake.pydecimal(3, 2, False, -180, 180)
        radar_id = "DN"
        object_class = "CA"

        r_event = RadarEvent.objects.create(
            timestamp=datetime.now(),
            velocity=velocity,
            latitude=latitude,
            longitude=longitude,
            radar_id=radar_id,
            object_class=object_class
        )

        self.assertEquals(r_event.velocity, velocity, "Velocity not equal!")
        self.assertEquals(r_event.latitude, latitude, "Latitude not equal!")
        self.assertEquals(r_event.longitude, longitude, "Longitude not equal!")
        self.assertEquals(r_event.radar_id, radar_id, "Radar_id not equal!")
        self.assertEquals(r_event.object_class, object_class, "Object Class not equal!")
