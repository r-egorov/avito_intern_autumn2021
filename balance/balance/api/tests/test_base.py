from django.test import TestCase
from ..models import Balance


class BaseTest(TestCase):
    user_ids = []

    @classmethod
    def setUpTestData(cls):
        balance = Balance.objects.create(user_id=1, balance=100)
        cls.user_ids.append(balance.user_id)

        balance = Balance.objects.create(user_id=2, balance=2000)
        cls.user_ids.append(balance.user_id)

        balance = Balance.objects.create(user_id=3, balance=500)
        cls.user_ids.append(balance.user_id)