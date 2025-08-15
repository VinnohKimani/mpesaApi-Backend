import os 
from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_cors import CORS
from models import db
from Resources.payment import (
    PaymentResource,
    PaymentCallbackResource,
    CheckPaymentResource,
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SQLALCHEMY_ECHO"] = True
app.config["BUNDLE_ERRORS"] = True

# setting up flask-restful
api = Api(app)

migrate = Migrate(app, db)
# Linking our db to our flask app
db.init_app(app)

api.add_resource(PaymentResource, "/payments")
api.add_resource(PaymentCallbackResource, "/payments/callback")
api.add_resource(CheckPaymentResource, "/payments/check/<string:checkout_request_id>")
