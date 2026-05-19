import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import pyrebase

import os
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# ADMIN SDK (DB)
# =========================

firebase_path = os.path.join(BASE_DIR, "firebase.json")
cred = credentials.Certificate(firebase_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://projet-S6-smart-home-default-rtdb.europe-west1.firebasedatabase.app/"
    })

root = db.reference("/")

# =========================
# AUTH CONFIG (PYREBASE)
# =========================

firebase_auth_path = os.path.join(BASE_DIR, "firebase_auth.json")

with open(firebase_auth_path, "r") as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# =========================
# DATABASE FUNCTIONS
# =========================

def get_data(path="/"):
    return root.child(path).get()


def set_data(path, data):
    root.child(path).set(data)


def update_data(path, data):
    root.child(path).update(data)


# =========================
# HISTORY
# =========================

def push_history(path, value):
    ref = db.reference(path)

    ref.push({
        "value": value,
        "timestamp": int(time.time())
    })


# =========================
# AUTH FUNCTIONS
# =========================

def register_user(email, password):

    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user

    except Exception as e:
        print("Erreur inscription :", e)
        return None


def login_user(email, password):

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user

    except Exception as e:
        print("Erreur connexion :", e)
        return None

firebase_config_data = firebase_config

def get_firebase_config():
    return firebase_config

print("Done !")