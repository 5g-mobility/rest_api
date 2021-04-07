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

    def test_blank_event_class(self):
        with self.assertRaises(ValidationError, msg={'location': "Location Barra and Costa Nova are only allowed for "
                                                                 "Condition or Carbon Footprint events"}):
            Event.objects.create(
                        location="CN",
                        event_type="RT",
                        velocity=fake.random_int(-300, 300)
                        )
