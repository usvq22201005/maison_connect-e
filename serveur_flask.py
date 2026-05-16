from flask import Flask, render_template, jsonify
import time
from firebase_control import get_data, update_data

app = Flask(__name__)

@app.route("/api/data")
def api_data():

    data = get_data("SmartHome")

    # ATTENTION
    if data["Garage"]["Capteurs"]["Ultrason"]["distance"] <= data["Garage"]["Actionneurs"]["LedStationnement"]["distance_activation"]:
        update_data("SmartHome/Garage/Actionneurs/LedStationnement", {"etat": True})
    else:
        update_data("SmartHome/Garage/Actionneurs/LedStationnement", {"etat": False})
    #A RETIRER UNE FOIS LA LED ARDUINO CORRECTEMENT SETUP

    return jsonify(data)




@app.route("/")
def home():

    data = get_data("SmartHome")
    return render_template("index.html", data=data)

# ROUTES

#Fonction qui prend en entrée ce que l'on souhaite envoyer en série à l'arduino, affiche dans la console si l'arduino n'est pas branché
def send_command(commande):
    if arduino_present:
        arduino.write(commande)
    else:
        print("Commande envoyée : ", commande)

@app.route("/salon_on")
def salon_on():
    #send_command(b'S')
    update_data("SmartHome/Salon/Actionneurs/Eclairage", {"etat": True})
    return "OK"

@app.route("/salon_off")
def salon_off():
    #send_command(b's')
    update_data("SmartHome/Salon/Actionneurs/Eclairage", {"etat": False})
    return "OK"

@app.route("/led_on")
def led_on():
    #send_command(b'L')
    update_data("SmartHome/Chambre_1/Actionneurs/Eclairage", {"etat": True})
    return "OK"

@app.route("/led_off")
def led_off():
    #send_command(b'l')
    update_data("SmartHome/Chambre_1/Actionneurs/Eclairage", {"etat": False})
    return "OK"

@app.route("/heat_on")
def heat_on():
    #send_command(b'H')
    update_data("SmartHome/Chambre_1/Actionneurs/Chauffage", {"etat": True})
    return "OK"

@app.route("/heat_off")
def heat_off():
    #send_command(b'h')
    update_data("SmartHome/Chambre_1/Actionneurs/Chauffage", {"etat": False})
    return "OK"

@app.route("/relay_on")
def relay_on():
    #send_command(b'R')
    update_data("SmartHome/Chambre_1/Actionneurs/Ventilateur", {"etat": True})
    return "OK"

@app.route("/relay_off")
def relay_off():
    #send_command(b'r')
    update_data("SmartHome/Chambre_1/Actionneurs/Ventilateur", {"etat": False})
    return "OK"

@app.route("/led2_on")
def led2_on():
    #send_command(b'K')
    update_data("SmartHome/Chambre_2/Actionneurs/Eclairage", {"etat": True})
    return "OK"

@app.route("/led2_off")
def led2_off():
    #send_command(b'k')
    update_data("SmartHome/Chambre_2/Actionneurs/Eclairage", {"etat": False})
    return "OK"

@app.route("/heat2_on")
def heat2_on():
    #send_command(b'J')
    update_data("SmartHome/Chambre_2/Actionneurs/Chauffage", {"etat": True})
    return "OK"

@app.route("/heat2_off")
def heat2_off():
    #send_command(b'j')
    update_data("SmartHome/Chambre_2/Actionneurs/Chauffage", {"etat": False})
    return "OK"

@app.route("/arm")
def arm():
    #send_command(b'A')
    update_data("SmartHome/Salon/Actionneurs/Alarme", {"etat": True})
    return "OK"

@app.route("/disarm")
def disarm():
    #send_command(b'a')
    update_data("SmartHome/Salon/Actionneurs/Alarme", {"etat": False})
    return "OK"

app.run(host='0.0.0.0', port=5000)
#http://127.0.0.1:5000/