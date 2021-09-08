from django.utils import timezone
from django.core import exceptions

from rest_framework import serializers

from .models import User, Balance, Transaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "created"]


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ["balance", "user", "last_update"]

    def to_representation(self, instance):
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

    def to_representation(self, instance):
        return {
            "data": {
                "amount": instance.amount,
                "source_id": instance.source,
                "target_id": instance.target,
                "comment": instance.comment,
                "timestamp": instance.timestamp
            }
        }


class ChangeBalanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)

    def to_internal_value(self, request_data):
        data = request_data.get("data")
        if not data:
            raise serializers.ValidationError({
                'data': ['This field is required.']
            })
        return super().to_internal_value(data)

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


class CreateUserSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=9, decimal_places=2)

    def to_internal_value(self, request_data):
        data = request_data.get("data")
        if not data:
            raise serializers.ValidationError({
                'data': ['This field is required.']
            })
        return super().to_internal_value(data)

    def validate_balance(self, balance):
        if balance < 0:
            raise serializers.ValidationError('Can\'t be negative.')
        return balance



class GetBalanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def to_internal_value(self, request_data):
        data = request_data.get("data")
        if not data:
            raise serializers.ValidationError({
                'data': ['This field is required.']
            })
        return super().to_internal_value(data)


class MakeTransferSerializer(serializers.Serializer):
    source_id = serializers.IntegerField()
    target_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)

    def to_internal_value(self, request_data):
        data = request_data.get("data")
        if not data:
            raise serializers.ValidationError({
                'data': ['This field is required.']
            })
        return super().to_internal_value(data)

    def validate_amount(self, amount):
        if amount < 0:
            raise serializers.ValidationError('Can\'t be negative.')
        return amount


