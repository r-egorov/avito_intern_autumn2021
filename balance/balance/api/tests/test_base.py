from django.test import TestCase
from ..models import User, Balance, Transaction


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = []
        user = User.objects.create()
        balance = Balance.objects.create(user=user)
        cls.users.append(user)

        user = User.objects.create()
        balance = Balance.objects.create(user=user)
        cls.users.append(user)

        user = User.objects.create()
        balance = Balance.objects.create(user=user)
        cls.users.append(user)