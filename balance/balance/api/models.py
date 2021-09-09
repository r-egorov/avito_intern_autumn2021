from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from typing import Dict


class Balance(models.Model):
    balance = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=False,
                                  validators=[MinValueValidator(0)])
    user_id = models.PositiveIntegerField(unique=True)
    last_update = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.balance < 0:
            raise ValidationError("Balance can't be negative")

    def __repr__(self):
        return f"<Balance (ID: {self.id})>"

    def __str__(self):
        return f"<Balance (ID: {self.id}, Balance: {self.balance})>"


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0, null=False,
                                 validators=[MinValueValidator(0)])
    source_id = models.PositiveIntegerField()
    target_id = models.PositiveIntegerField()
    comment = models.TextField(max_length=4096)
    timestamp = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return f"<Transaction (ID: {self.id})>"

    def __str__(self):
        return f"<Transaction (ID: {self.id})>"
