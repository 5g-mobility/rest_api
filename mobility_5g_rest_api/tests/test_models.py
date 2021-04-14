from django.core.exceptions import ValidationError
from django.test import TestCase

from faker import Faker

from mobility_5g_rest_api.models import Event

fake = Faker()


class EventTest(TestCase):
    def setUpTestData(cls):
        pass
        # cls.timestamp = fake

    def tearDown(self):
        pass

    # testes para clean

    # testes para ver se guarda na bd:
    # 1 teste inflow, 1 teste climate, 1 teste event
    def test_cn_ba_location(self):
        with self.assertRaises(ValidationError, msg={'location': "Location Barra and Costa Nova are only allowed for "
                                                                 "Condition or Carbon Footprint events"}):
            Event.objects.create(
                        location="CN",
                        event_type="RT",
                        velocity=fake.random_int(-300, 300)
                        )

    def test_event_class_conditions(self):
        with self.assertRaises(ValidationError, msg={'event_type': 'Event_class Rain, Fog, No Light, Light, Outside Temperature and Car Speeding are only allowed for the Conditions event type'}):
            Event.objects.create(
                location="RA",
                event_type="RT",
                event_class="CS",
                velocity=fake.random_int(-300, 300)
            )

    def test_cf_co_not_allowed_locations(self):
        with self.assertRaises(ValidationError, msg={'location': 'Location Ria Ativa, Duna, Ponte da Barra and A25 '
                                                                 'are not allowed for Conditions or Carbon Footprint '
                                                                 'events'}):
            Event.objects.create(
                location="RA",
                event_type="CO",
                event_class="LT",
                velocity=fake.random_int(-300,300)
            )

    def test_an_pe_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={'event_type': 'Event_class Animal and Person are only allowed for the Bike Lanes or Road Danger event type'}):
            Event.objects.create(
                location="RA",
                event_type="RT",
                event_class="AN",
                velocity=fake.random_int(-300, 300)
            )

    def test_bc_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_type': 'Event_class Bicycle is only allowed for the Bike Lanes or Road Traffic event type'}):
            Event.objects.create(
                location="DN",
                event_type="RD",
                event_class="BC",
                velocity=fake.random_int(-300, 300)
            )

    def test_ca_mc_tr_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_type': 'Event_class Car, Motorcycle and Truck are only allowed for the Road Traffics event type'}):
            Event.objects.create(
                location="PT",
                event_type="RD",
                event_class="CA",
                velocity=fake.random_int(-300, 300)
            )

    def test_latitude_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'latitude': 'Latitude is only allowed when type is Carbon Footprint or Conditions'}):
            Event.objects.create(
                location="PT",
                event_type="RT",
                event_class="CA",
                latitude=80,
                velocity=fake.random_int(-300, 300)
            )

    def test_longitude_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'longitude': 'Longitude is only allowed when type is Carbon Footprint or Conditions'}):
            Event.objects.create(
                location="PT",
                event_type="RT",
                event_class="CA",
                longitude=120,
                velocity=fake.random_int(-300, 300)
            )

    def test_blank_event_class(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_class': 'Blank is only allowed when type is Carbon Footprint'}):
            Event.objects.create(
                location="PT",
                event_type="RT",
                velocity=fake.random_int(-300, 300)
            )

    def test_co2_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'co2km': 'CO2km is only allowed when type is Carbon Footprint'}):
            Event.objects.create(
                location="PT",
                event_type="RT",
                event_class="CA",
                co2km=200.01,
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
                latitude=80,
                longitude=120,
                velocity=fake.random_int(-300, 300)
            )

    def test_temperature_not_allowed_event_class(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'temperature': 'Temperature is only allowed when type is Conditions and class Outside Temperature'}):
            Event.objects.create(
                location="BA",
                event_type="CO",
                event_class="FO",
                latitude=80,
                longitude=120,
                velocity=fake.random_int(-300, 300)
            )

    def test_so_sc_not_allowed_event_type(self):
        with self.assertRaises(ValidationError,
                               msg={
                                   'event_type': 'Event_class Strange Objects or Stopped Car are only allowed for event_type Road Danger'}):
            Event.objects.create(
                location="PT",
                event_type="RT",
                event_class="SO",
                velocity=fake.random_int(-300, 300)
            )