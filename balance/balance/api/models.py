from django.db import models
from django.utils import timezone


class User(models.Model):
    def __repr__(self):
        return f"<User (ID: {self.id})>"

    def __str__(self):
        return f"<User (ID: {self.id})>"


class Balance(models.Model):
    balance = models.PositiveIntegerField(default=0, null=False)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)

    def __repr__(self):
        return f"<Balance (ID: {self.id})>"

    def __str__(self):
        return f"<Balance (ID: {self.id})>"


class Transaction(models.Model):
    amount = models.IntegerField(default=0, null=False)
    source = models.ForeignKey(Balance, on_delete=models.RESTRICT, related_name="source")
    target = models.ForeignKey(Balance, on_delete=models.RESTRICT, related_name="target")
    comment = models.CharField(max_length=4096)
    timestamp = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return f"<Transaction (ID: {self.id})>"

    def __str__(self):
        return f"<Transaction (ID: {self.id})>"
