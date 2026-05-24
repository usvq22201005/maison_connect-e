from flask import Flask, render_template, jsonify, request, redirect, session
import time
from firebase_control import *

app = Flask(__name__)

app.secret_key = get_firebase_config()["secret_key"]

@app.route("/api/data")
def api_data():

    user_id = session.get("user_id")
    home_id = get_user_home(user_id)

    data = get_data(f"Homes/{home_id}")

    return jsonify(data)




@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")
    

    data = get_data(f"Homes/{session["home_id"]}")
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


#Historique
@app.route("/api/history/<room>/<sensor>/<metric>")
def history(room, sensor, metric):

    path = f"Homes/{session["home_id"]}/{room}/Capteurs/{sensor}/Historique/{metric}"
    data = get_data(path)

    if not data:
        return jsonify([])

    result = [
        {
            "x": v.get("timestamp", 0),
            "y": v.get("value", 0)
        }
        for v in data.values()
        if isinstance(v, dict)
    ]

    return jsonify(result)

@app.route("/toggle/<room>/<actuator>/<state>")
def toggle(room, actuator, state):

    user_id = session.get("user_id")
    home_id = get_user_home(user_id)

    path = f"Homes/{home_id}/{room}/Actionneurs/{actuator}/etat"

    update_data(path, state == "true")

    return "ok"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = login_user(email, password)

        if user:
            session["user"] = email
            session["user_id"] = user["localId"]
            session["home_id"] = get_user_home(session["user_id"])
            return redirect("/")

        return "Erreur connexion"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = register_user(email, password)

        if user:
            return redirect("/login")

        return "Erreur inscription"

    return render_template("register.html")


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


def run_flask():
    app.run(host='0.0.0.0', port=5000)
    #http://127.0.0.1:5000/
    #