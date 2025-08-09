import os
import base64
import requests

from requests.auth import HTTPBasicAuth
from datetime import datetime


class Mpesa:
    # class attributes
    consumer_key = None
    consumer_secret = None
    business_short_code = "174379"
    timestamp = None

    def __init__(self):
        self.consumer_key = os.environ.get("CONSUMER_KEY")
        self.consumer_secret = os.environ.get("CONSUMER_SECRET")
        self.saf_pass_key = os.environ.get("SAF_PASS_KEY")
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.access_token = None

    def get_access_token(self):
        """
        -> Generating  access tokens that will be used in subsequent request
        to mpesa
        """
        # check if access token exists
        if self.access_token:
            return self.access_token
        # If not get a new one from saf
        res = requests.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            #  Combine consumer_key and consumer_secrete
            auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
        )

        data = res.json()
        self.access_token = data["access_token"]
        print(data)

        return self.access_token

    def generate_password(self):
        """
        Generating Passowrd by combinning business_short_code, saf_pass_key and timestamp
        """
        password_str = self.business_short_code + self.saf_pass_key + self.timestamp
        return base64.b64encode(password_str.encode()).decode("utf-8")

    def make_stk_push(self, data):
        phone = data["phone"]
        amount = data["amount"]
        desc = data["description"]

        body = {
            "BusinessShortCode": self.business_short_code,
            "Password": self.generate_password(),
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": self.business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://11d88585c5e2.ngrok-free.app/payments/callback",
            "AccountReference": "Test",
            "TransactionDesc": desc,
        }
        token = self.get_access_token()
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        response_data = response.json()
        return response_data

    def check_transaction(self, checkout_request_id):
        data = {
            "BusinessShortCode": self.business_short_code,
            "Password": self.generate_password(),
            "Timestamp": self.timestamp,
            "CheckoutRequestID": checkout_request_id,
        }

        token = self.get_access_token()
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query",
            json=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        return response.json()
