from django.core import exceptions

from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from .serializers import UserSerializer, BalanceSerializer, ChangeBalanceSerializer, GetBalanceSerializer, \
    MakeTransferSerializer, CreateUserSerializer
from .models import User, Balance, Transaction


class CreateUser(APIView):
    resource_name = "create_user"
    parser_classes = [JSONParser]

    @transaction.atomic()
    def post(self, request) -> Response:
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create()

            balance_amount = serializer.validated_data.get("balance")
            balance_amount = balance_amount if balance_amount else 0
            balance = Balance.objects.create(user=user, balance=balance_amount)

            return Response(UserSerializer(user).data,
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeBalance(APIView):
    resource_name = "change_balance"
    parser_classes = [JSONParser]

    @transaction.atomic()
    def post(self, request) -> Response:
        serializer = ChangeBalanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        uid = serializer.data.get("id")

        try:
            balance = Balance.objects.get(user=uid)
        except Balance.DoesNotExist:
            return Response({"errors": {"id": ["No user with such ID found"]}},
                            status=status.HTTP_404_NOT_FOUND)

        serializer.update(balance, serializer.validated_data)

        amount = serializer.validated_data.get("amount")
        comment = "Deposit" if amount > 0 else "Withdrawal"
        user = balance.user
        trans = Transaction.objects.create(
            amount=abs(amount), source=user, target=user, comment=comment
        )

        return Response(BalanceSerializer(balance).data,
                        status=status.HTTP_200_OK)


class GetBalance(APIView):
    resource_name = "get_balance"

    def post(self, request) -> Response:
        serializer = GetBalanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        uid = serializer.data.get("id")

        try:
            balance = Balance.objects.get(user=uid)
        except Balance.DoesNotExist:
            return Response({"errors": {"id": ["No user with such ID found"]}},
                            status=status.HTTP_404_NOT_FOUND)

        return Response(BalanceSerializer(balance).data, status=status.HTTP_200_OK)


class MakeTransfer(APIView):
    resource_name = "make-transfer"

    @transaction.atomic()
    def post(self, request) -> Response:
        serializer = MakeTransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        ids = {
            "source_id": serializer.data.get("source_id"),
            "target_id": serializer.data.get("target_id")
        }
        balances = []

        for key in ids:
            try:
                balances.append(Balance.objects.get(user=ids[key]))
            except Balance.DoesNotExist:
                return Response({"errors": {key: ["No user with such ID found"]}},
                                status=status.HTTP_404_NOT_FOUND)

        source_balance = balances[0]
        target_balance = balances[1]
        amount = serializer.validated_data.get("amount")

        source_balance.balance -= amount
        source_balance.last_update = timezone.now()
        try:
            source_balance.clean_fields()
        except exceptions.ValidationError:
            return Response({"errors": {
                "source_id": ["This balance would be negative after the transfer"]
            }},
                status=status.HTTP_400_BAD_REQUEST)

        target_balance.balance += amount
        target_balance.last_update = timezone.now()

        source_balance.save()
        target_balance.save()

        trans = Transaction.objects.create(
            amount=abs(amount),
            source=source_balance.user,
            target=target_balance.user,
            comment="Transfer"
        )

        return Response({"status": "OK"}, status=status.HTTP_200_OK)
