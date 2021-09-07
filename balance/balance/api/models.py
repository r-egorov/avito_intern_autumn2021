from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

from typing import Dict
from decimal import Decimal


class User(models.Model):
    created = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return f"<User (ID: {self.id})>"

    def __str__(self):
        return f"<User (ID: {self.id})>"


class Balance(models.Model):
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=False,
                                  validators=[MinValueValidator(0)])
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    last_update = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return f"<Balance (ID: {self.id})>"

    def __str__(self):
        return f"<Balance (ID: {self.id})>"

    def render_dict(self) -> Dict:
        return {
            "balance": self.balance,
            "user_id": self.user.id,
            "last_update": self.last_update
        }


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=False,
                                 validators=[MinValueValidator(0)])
    source = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="source")
    target = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="target")
    comment = models.CharField(max_length=4096)
    timestamp = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return f"<Transaction (ID: {self.id})>"

    def __str__(self):
        return f"<Transaction (ID: {self.id})>"
