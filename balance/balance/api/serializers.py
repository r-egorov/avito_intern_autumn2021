from decimal import Decimal

from django.utils import timezone
from django.core import exceptions

from rest_framework import serializers

from .models import Balance, Transaction


class MyBaseSerializer(serializers.Serializer):
    """
    A Base class for serializers
    Validates if the data in JSON was wrapped in "data" field
    """
    def to_internal_value(self, request_data):
        data = request_data.get("data")
        if not data:
            raise serializers.ValidationError({
                'data': ['This field is required.']
            })
        return super().to_internal_value(data)


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ["balance", "user_id", "last_update"]

    # def to_representation(self, instance: Balance):
    #     return {
    #         "user_id": instance.user_id,
    #         "balance": instance.balance,
    #         "last_update": instance.last_update
    #     }


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["amount", "source_id", "target_id", "comment", "timestamp"]

    # def to_representation(self, instance: Transaction):
    #     return {
    #         "amount": instance.amount,
    #         "source_id": instance.source_id,
    #         "target_id": instance.target_id,
    #         "comment": instance.comment,
    #         "timestamp": instance.timestamp
    #     }


class ChangeBalanceSerializer(MyBaseSerializer):
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)

    def update(self, instance: Balance, validated_data):
        instance.balance += validated_data.pop("amount")
        instance.last_update = timezone.now()
        try:
            instance.clean_fields()
        except exceptions.ValidationError:
            raise serializers.ValidationError({
                'balance': ['Would be negative after the operation.']
            })
        instance.save()
        return instance


class GetBalanceSerializer(MyBaseSerializer):
    user_id = serializers.IntegerField()


class GetTransactionsSerializer(MyBaseSerializer):
    user_id = serializers.IntegerField()
    sort_by = serializers.CharField()


class MakeTransferSerializer(MyBaseSerializer):
    source_id = serializers.IntegerField()
    target_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)

    def validate_amount(self, amount: Decimal) -> Decimal:
        if amount < 0:
            raise serializers.ValidationError('Can\'t be negative.')
        return amount
