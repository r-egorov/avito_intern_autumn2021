import json

from django.urls import reverse

from .test_base import BaseTest
from ..models import User, Balance, Transaction


class TestViews(BaseTest):
    def test_get_balance_no_data_field(self):
        payload = {
            "daata": {
                "id": 12
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_create_user_without_balance(self):
        payload = {
            "data": {}
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("create-user"),
                               data=payload,
                               content_type="application/json")

        self.assertEqual(res.status_code, 201)

        id = res.data.get("id")
        balance = Balance.objects.get(user=id)
        self.assertEqual(balance.balance, 0)

