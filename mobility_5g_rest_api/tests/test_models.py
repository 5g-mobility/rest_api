from django.core.exceptions import ValidationError
from django.test import TestCase

from faker import Faker

from mobility_5g_rest_api.models import Event

fake = Faker()


class EventTest(TestCase):
    def setUpTestData(cls):
        pass
        # cls.timestamp = fake

    def test_blank_event_class(self):
        # In test methods, use the variables created above
        self.assertRaises(ValidationError, Event.objects.create(
            location="CN",
            event_type="RT",
            velocity=fake.random_int(-300, 300)
            )
                          )
