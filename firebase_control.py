import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
firebase_path = os.path.join(BASE_DIR, "firebase.json")
cred = credentials.Certificate(firebase_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://projet-S6-smart-home-default-rtdb.europe-west1.firebasedatabase.app/"
    })

root = db.reference("/")


#Lecture
def get_data(path="/"):
    return root.child(path).get()


#Ecriture
def set_data(path, data):
    root.child(path).set(data)


#Mise a jour
def update_data(path, data):
    root.child(path).update(data)

print("Done !")