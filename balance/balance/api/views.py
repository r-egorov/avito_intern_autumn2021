from abc import abstractmethod
from typing import List, Dict
from decimal import Decimal

from django.core import exceptions

from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.serializers import BaseSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from .serializers import UserSerializer, BalanceSerializer, \
    ChangeBalanceSerializer, GetBalanceSerializer, \
    MakeTransferSerializer, TransactionSerializer
from .models import User, Balance, Transaction
from .exceptions import BalanceDoesNotExist


class BaseView(APIView):
    """
    Base class for views - takes a post request, validates data
    with the child-specific serializer
    """
    parser_classes = [JSONParser]
    serializer = BaseSerializer

    @transaction.atomic()
    def post(self, request) -> Response:
        errors = {}
        serializer = self.serializer(data=request.data)
        if not serializer.is_valid():
            errors["errors"] = serializer.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return self.handler(serializer)

    @abstractmethod
    def handler(self, serializer) -> Response:
        pass

    @staticmethod
    def get_balances(serializer: BaseSerializer, *args: str) -> List[Balance]:
        """
        Takes names of user_id-fields in JSON as arguments,
        returns a list of Balance-instances for these users.
        Raises BalanceDoesNotExist if no balance found.
        :param serializer - a serializer needed for processing JSON
        :param args: strings - names of fields in JSON
        :return: list of Balance instances
        """
        ids = {}
        balances = []

        for field_name in args:
            ids[field_name] = serializer.data.get(field_name)

        for key in ids:
            try:
                balances.append(Balance.objects.get(user=ids[key]))
            except Balance.DoesNotExist:
                raise BalanceDoesNotExist(key)
        return balances


class CreateUser(BaseView):
    serializer = UserSerializer
    resource_name = "create_user"

    @transaction.atomic()
    def handler(self, serializer) -> Response:
        payload = {}
        http_status = status.HTTP_200_OK

        serializer.save()
        payload = serializer.data
        return Response(payload, status=http_status)


class ChangeBalance(BaseView):
    serializer = ChangeBalanceSerializer
    resource_name = "change_balance"

    @staticmethod
    def do_transaction(user: User, amount: Decimal):
        """
        Takes a User-instance and creates a Transaction-instance
        with the amount
        :param user: User-instance
        :param amount: Decimal - amount of Transaction
        """
        comment = "Deposit" if amount > 0 else "Withdrawal"
        Transaction.objects.create(
            amount=abs(amount), source=user, target=user, comment=comment
        )

    @transaction.atomic()
    def handler(self, serializer) -> Response:
        payload = {}
        http_status = status.HTTP_200_OK

        try:
            balance: Balance = self.get_balances(serializer, "id")[0]
            serializer.update(balance, serializer.validated_data)
            self.do_transaction(balance.user,
                                serializer.validated_data.get("amount"))
            payload = BalanceSerializer(balance).data
        except BalanceDoesNotExist as e:
            http_status = status.HTTP_404_NOT_FOUND
            payload = {"errors": {e.field_name: ["No user with such ID found"]}}

        return Response(payload, status=http_status)


class GetBalance(BaseView):
    serializer = GetBalanceSerializer
    resource_name = "get_balance"

    def handler(self, serializer) -> Response:
        payload = {}
        http_status = status.HTTP_200_OK

        try:
            balance: Balance = self.get_balances(serializer, "id")[0]
            payload = BalanceSerializer(balance).data
        except BalanceDoesNotExist as e:
            http_status = status.HTTP_404_NOT_FOUND
            payload = {"errors": {e.field_name: ["No user with such ID found"]}}

        return Response(payload, status=http_status)


class MakeTransfer(BaseView):
    serializer = MakeTransferSerializer
    resource_name = "make-transfer"

    @staticmethod
    def do_transaction(source_balance: Balance,
                       target_balance: Balance,
                       amount: Decimal) -> Transaction:
        """
        Takes two Balance-instances, transfers amount from source to target.
        Raises exception if source becomes negative.
        Returns a Transaction-instance.
        :param source_balance: Balance instance to transfer from
        :param target_balance: Balance instance to transfer to
        :param amount: Decimal - amount to transfer
        :return: Transaction instance
        """
        source_balance.balance -= amount
        source_balance.last_update = timezone.now()
        source_balance.clean_fields()

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
        return trans

    @transaction.atomic()
    def handler(self, serializer) -> Response:
        payload = {}
        http_status = status.HTTP_200_OK

        try:
            balances: List[Balance] = self.get_balances(serializer, "source_id", "target_id")
            amount: Decimal = serializer.validated_data.get("amount")
            trans: Transaction = self.do_transaction(balances[0], balances[1], amount)
            payload = TransactionSerializer(trans).data
        except BalanceDoesNotExist as e:
            payload = {"errors": {e.field_name: ["No user with such ID found"]}}
            http_status = status.HTTP_404_NOT_FOUND
        except exceptions.ValidationError:
            payload = {
                "errors": {"source_id": ["This balance would be negative after the transfer"]}
            }
            http_status = status.HTTP_400_BAD_REQUEST

        return Response(payload, status=http_status)
