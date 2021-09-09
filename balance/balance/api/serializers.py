from decimal import Decimal

from django.utils import timezone
from django.core import exceptions

from rest_framework import serializers

from .models import User, Balance, Transaction


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


class UserSerializer(serializers.ModelSerializer, MyBaseSerializer):
    balance = serializers.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        model = User
        fields = ["id", "created", "balance"]

    def validate_balance(self, balance: Decimal) -> Decimal:
        if balance < 0:
            raise serializers.ValidationError('Can\'t be negative.')
        return balance

    def create(self, validated_data) -> User:
        balance: Decimal = validated_data.pop("balance")
        user = User.objects.create()
        Balance.objects.create(user=user, balance=balance)
        return user

    def to_representation(self, instance: User):
        return {
            "data": {
                "id": instance.id,
                "created": instance.created
            }
        }


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ["balance", "user", "last_update"]

    def to_representation(self, instance: Balance):
        return {
            "data": {
                "user_id": instance.user.id,
                "balance": instance.balance,
                "last_update": instance.last_update
            }
        }


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["amount", "source", "target", "comment", "timestamp"]

    def to_representation(self, instance: Transaction):
        return {
            "data": {
                "amount": instance.amount,
                "source_id": instance.source.id,
                "target_id": instance.target.id,
                "comment": instance.comment,
                "timestamp": instance.timestamp
            }
        }


class ChangeBalanceSerializer(MyBaseSerializer):
    id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)

    def update(self, instance: Balance, validated_data):
        instance.balance += validated_data.get("amount")
        instance.last_update = timezone.now()
        try:
            instance.clean_fields()
        except exceptions.ValidationError:
            raise serializers.ValidationError({
                'balance': ['Can\'t be negative.']
            })
        instance.save()
        return instance


class GetBalanceSerializer(MyBaseSerializer):
    id = serializers.IntegerField()


class MakeTransferSerializer(MyBaseSerializer):
    source_id = serializers.IntegerField()
    target_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)

    def validate_amount(self, amount: Decimal) -> Decimal:
        if amount < 0:
            raise serializers.ValidationError('Can\'t be negative.')
        return amount
