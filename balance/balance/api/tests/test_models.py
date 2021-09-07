from django.db import models

from .test_base import BaseTest
from ..models import User, Balance, Transaction


class TestModels(BaseTest):
    def test_balance_not_deleted_with_user(self):
        user = self.users[0]
        balance = Balance.objects.get(user=user)
        self.assertTrue(balance)

        try:
            user.delete()
        except models.deletion.RestrictedError:
            pass

        self.assertTrue(User.objects.get(pk=user.id))
        self.assertTrue(Balance.objects.get(user=user))

    def test_transaction_not_deleted_with_source_or_target(self):
        user1 = self.users[0]
        user2 = self.users[1]
        balance1 = Balance.objects.get(user=user1)
        balance2 = Balance.objects.get(user=user2)

        balance1.balance += 500
        balance1.save()
        balance2.balance += 300
        balance2.save()

        trans = Transaction.objects.create(source=user1, target=user2, amount=400)

        try:
            user1.delete()
        except models.deletion.RestrictedError:
            pass

        try:
            user2.delete()
        except models.deletion.RestrictedError:
            pass

        self.assertTrue(Transaction.objects.get(pk=trans.id))
        self.assertTrue(Balance.objects.get(pk=user1.id))
        self.assertTrue(Balance.objects.get(pk=user2.id))
