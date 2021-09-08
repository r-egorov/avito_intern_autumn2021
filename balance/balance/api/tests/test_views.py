import json

from django.urls import reverse

from .test_base import BaseTest
from ..models import User, Balance, Transaction


class TestViews(BaseTest):
    def test_create_user_without_balance(self):
        """
        Has to return a 201 CREATED HTTP-response,
        create a user with zero balance
        """
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

    def test_get_balance_no_data_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
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

    def test_get_balance_no_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response
        """
        payload = {
            "data": {
                "iid": 12
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_get_balance_no_such_user(self):
        """
        Has to return 404 NOT FOUND HTTP-response
        """
        payload = {
            "data": {
                "id": 12
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

    def test_get_balance_ok(self):
        """
        Has to return 200 OK HTTP-response and the balance of the user
        """
        payload = {
            "data": {
                "id": self.users[1].id
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("get-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.data.get("data")
        self.assertEqual(data.get("balance"), 2000)

    def test_change_balance_no_data_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user=self.users[1])
        payload = {
            "daata": {
                "id": self.users[1].id,
                "amount": 2000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)
        updated_balance = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_no_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user=self.users[1])
        payload = {
            "data": {
                "iid": self.users[1].id,
                "amount": 2000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)
        updated_balance = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_no_amount_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user=self.users[1])
        payload = {
            "data": {
                "id": self.users[1].id,
                "amoount": 2000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)
        updated_balance = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_no_such_user(self):
        """
        Has to return 404 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        payload = {
            "data": {
                "id": 999,
                "amount": 3000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

    def test_change_balance_overdraft(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance = Balance.objects.get(user=self.users[1])
        payload = {
            "data": {
                "id": self.users[1].id,
                "amount": -999999
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance.balance, initial_balance.balance)

    def test_change_balance_ok(self):
        """
        Has to return 200 OK HTTP-response and change the balance
        """
        initial_balance = Balance.objects.get(user=self.users[1])
        payload = {
            "data": {
                "id": self.users[1].id,
                "amount": 5000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("change-balance"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        updated_balance = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance.balance - initial_balance.balance, 5000)

    def test_make_transfer_no_data_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user=self.users[0])
        initial_balance1 = Balance.objects.get(user=self.users[1])

        payload = {
            "daata": {
                "source_id": self.users[1].id,
                "target_id": self.users[0].id,
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user=self.users[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_source_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user=self.users[0])
        initial_balance1 = Balance.objects.get(user=self.users[1])

        payload = {
            "data": {
                "soource_id": self.users[1].id,
                "target_id": self.users[0].id,
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user=self.users[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_target_id_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user=self.users[0])
        initial_balance1 = Balance.objects.get(user=self.users[1])

        payload = {
            "data": {
                "source_id": self.users[1].id,
                "taarget_id": self.users[0].id,
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user=self.users[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_amount_field(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user=self.users[0])
        initial_balance1 = Balance.objects.get(user=self.users[1])

        payload = {
            "data": {
                "source_id": self.users[1].id,
                "target_id": self.users[0].id,
                "ammount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user=self.users[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_no_such_user(self):
        """
        Has to return 404 NOT FOUND HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user=self.users[0])

        payload = {
            "data": {
                "source_id": 99999,
                "target_id": self.users[0].id,
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

        updated_balance0 = Balance.objects.get(user=self.users[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        initial_balance1 = Balance.objects.get(user=self.users[1])

        payload = {
            "data": {
                "source_id": self.users[1].id,
                "target_id": 99999,
                "amount": 300
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 404)

        updated_balance1 = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_overdraft(self):
        """
        Has to return 400 BAD REQUEST HTTP-response,
        make no changes to the database
        """
        initial_balance0 = Balance.objects.get(user=self.users[0])
        initial_balance1 = Balance.objects.get(user=self.users[1])

        payload = {
            "data": {
                "source_id": self.users[1].id,
                "target_id": self.users[0].id,
                "amount": 9999999
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

        updated_balance0 = Balance.objects.get(user=self.users[0])
        self.assertEqual(updated_balance0.balance, initial_balance0.balance)

        updated_balance1 = Balance.objects.get(user=self.users[1])
        self.assertEqual(updated_balance1.balance, initial_balance1.balance)

    def test_make_transfer_ok(self):
        """
        Has to return 200 OK HTTP-response and change the balances
        """
        initial_balance0 = Balance.objects.get(user=self.users[0])
        initial_balance1 = Balance.objects.get(user=self.users[1])

        payload = {
            "data": {
                "source_id": self.users[1].id,
                "target_id": self.users[0].id,
                "amount": 1000
            }
        }
        payload = json.dumps(payload)
        res = self.client.post(reverse("make-transfer"),
                               data=payload,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)

        updated_balance0 = Balance.objects.get(user=self.users[0])
        self.assertEqual(updated_balance0.balance - initial_balance0.balance, 1000)

        updated_balance1 = Balance.objects.get(user=self.users[1])
        self.assertEqual(initial_balance1.balance - updated_balance1.balance, 1000)
