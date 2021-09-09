from django.db import models
from django.core import exceptions

from .test_base import BaseTest
from ..models import Balance, Transaction


class TestModels(BaseTest):
    def test_balance_not_created_with_negative_amount(self):
        balance = Balance(balance=-5000, user_id=50)
        with self.assertRaises(exceptions.ValidationError):
            balance.clean_fields()

    def test_transaction_not_created_with_negative_amount(self):
        trans = Transaction(source_id=self.user_ids[1], target_id=self.user_ids[2], amount=-500)
        with self.assertRaises(exceptions.ValidationError):
            trans.clean_fields()
