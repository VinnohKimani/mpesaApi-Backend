from flask import request
from flask_restful import Resource
from datetime import datetime
from mpesa import Mpesa
from models import Payment, db


class PaymentResource(Resource):
    def post(self):
        mpesa_instance = Mpesa()
        req_data = request.get_json()

        phone = req_data.get("phone")
        amount = req_data.get("amount")
        if not phone:
            return {"message": "Phone number is required!"}, 400
        if not amount:
            return {"message": "Amount is required!"}, 400

        data = {
            "phone": phone,
            "amount": req_data.get("amount"),
            "description": "Shiko's Baby Shop",
        }

        mpesa_response = mpesa_instance.make_stk_push(data)

        return {"message": "Response Okay", "data": mpesa_response}


class CheckPaymentResource(Resource):
    def get(self, checkout_request_id):
        mpesa_instance = Mpesa()

        response = mpesa_instance.check_transaction(checkout_request_id)

        return {"message": "ok", "data": response}


class PaymentCallbackResource(Resource):
    def post(self):
        data = request.get_json()
        # Debugging
        print("Callback Data:", data)

        # Safaricom nests the info inside Body -> stkCallback
        stk_callback = data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")

        # Only save if payment was successful
        if result_code == 0:
            callback_items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            mpesa_data = {item["Name"]: item.get("Value") for item in callback_items}

            payment = Payment(
                phone_number=mpesa_data.get("PhoneNumber"),
                amount=mpesa_data.get("Amount"),
                transaction_code=mpesa_data.get("MpesaReceiptNumber"),
                transaction_date=datetime.strptime(
                    str(mpesa_data.get("TransactionDate")), "%Y%m%d%H%M%S"
                ),
            )

            db.session.add(payment)
            db.session.commit()

        return {"ResultCode": 0, "ResultDesc": "Accepted"}
