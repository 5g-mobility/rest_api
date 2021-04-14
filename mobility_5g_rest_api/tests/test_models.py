from django.core.exceptions import ValidationError
from django.test import TestCase

from faker import Faker

from mobility_5g_rest_api.models import Event, Climate, DailyInflow

fake = Faker()


class EventTest(TestCase):
    def setUpTestData(cls):
        pass

    def tearDown(self):
        pass

    def test_event_creation(self):
        location = "DN"
        event_type = "RT"
        event_class = "CA"
        velocity = fake.random_int(-300, 300)
        ev = Event.objects.create(
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
                location="CN",
                event_type="RT",
                velocity=fake.random_int(-300, 300)
            )

    def test_event_class_conditions(self):
        with self.assertRaises(ValidationError, msg={
                'event_type': 'Event_class Rain, Fog, No Light, Light, Outside Temperature, Car Speeding and Carbon '
                              'Footprint are only allowed for the Conditions event type'}):
            Event.objects.create(
                location="RA",
                event_type="RT",
                event_class="CS",
                velocity=fake.random_int(-300, 300)
            )

    def test_cf_co_not_allowed_locations(self):
        with self.assertRaises(ValidationError, msg={'location': 'Location Ria Ativa, Duna, Ponte da Barra and A25 '
                                                                 'are not allowed for Conditions events'}):
            Event.objects.create(
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
                location="PT",
                event_type="RD",
                event_class="CA",
                velocity=fake.random_int(-300, 300)
            )

    def test_latitude_longitude_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'latitude': 'Latitude is only allowed when event type is Conditions'}) and self.assertRaises(ValidationError,
                               msg={
                                   'longitude': 'Longitude is only allowed when event type is Conditions'}):
            Event.objects.create(
                location="PT",
                event_type="RT",
                event_class="CA",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                velocity=fake.random_int(-300, 300)
            )

    def test_co2_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'co2km': 'CO2km is only allowed when type is Conditions and class is Carbon '
                                            'Footprint'}):
            Event.objects.create(
                location="PT",
                event_type="CO",
                event_class="FO",
                latitude=fake.pydecimal(2, 2, False, -90, 90),
                longitude=fake.pydecimal(3, 2, False, -180, 180),
                co2km=fake.pydecimal(3, 2, True),
                velocity=fake.random_int(-300, 300)
            )

    def test_co2_not_given(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'co2km': 'CO2km needs to have value'}):
            Event.objects.create(
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
                location="PT",
                event_type="RT",
                event_class="SO",
                velocity=fake.random_int(-300, 300)
            )


class ClimateTest(TestCase):
    def setUpTestData(cls):
        pass

    def tearDown(self):
        pass

    def test_climate_creation(self):
        condition = "FG"
        daytime = fake.pybool()
        temperature = fake.pydecimal(2, 2, False)
        cl = Climate.objects.create(
            condition=condition,
            daytime=daytime,
            temperature=temperature,
        )
        self.assertEquals(cl.condition, condition, "Condition not equal!")
        self.assertEquals(cl.daytime, daytime, "Daytime not equal!")
        self.assertEquals(cl.temperature, temperature,
                          "Temperature not equal!")


class DailyInflowTest(TestCase):
    def setUpTestData(cls):
        pass

    def tearDown(self):
        pass

    def test_daily_inflow_creation(self):
        maximum = fake.random_int(100, 300)
        current = fake.random_int(0, 99)
        dl = DailyInflow.objects.create(
            maximum=maximum,
            current=current,
        )
        self.assertEquals(dl.maximum, maximum, "Maximum not equal!")
        self.assertEquals(dl.current, current, "Current not equal!")

    def test_daily_inflow_maximum_less_than_current(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'maximum': 'Maximum value needs to be higher or equals to current'}):
            DailyInflow.objects.create(
                maximum=2,
                current=100,
            )
