from django.core import exceptions

from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser

from typing import Dict, Optional

from .serializers import UserSerializer, BalanceSerializer, ChangeBalanceSerializer, GetBalanceSerializer
from .models import User, Balance, Transaction


class CreateUser(APIView):
    resource_name = "create_user"
    parser_classes = [JSONParser]

    @transaction.atomic()
    def post(self, request) -> Response:
        data = request.data.get("data")

        user_serializer = UserSerializer(data=data)
        if user_serializer.is_valid():
            user = user_serializer.save()

            balance_amount = data.get("balance")
            balance_amount = balance_amount if balance_amount else 0
            Balance.objects.create(user=user, balance=balance_amount)

            return Response(UserSerializer(user).data,
                            status=status.HTTP_201_CREATED)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        serializer = BalanceSerializer(balance)
        return Response(serializer.data, status=status.HTTP_200_OK)