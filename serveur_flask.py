from flask import Flask, render_template, jsonify, request, redirect, session
import time
from firebase_control import *
from vip_club import VIP_CLUB

app = Flask(__name__)

app.secret_key = get_firebase_config()["secret_key"]
login_attempts = {}

def is_authorized(email):
    return email in VIP_CLUB

@app.route("/api/data")
def api_data():

    data = get_data("SmartHome")

    return jsonify(data)




@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    email = session["user"]

    # Utilisateur autorisé
    if is_authorized(email):

        data = get_data("SmartHome")

        return render_template(
            "index.html",
            data=data,
            email=email
        )

    # Utilisateur NON autorisé
    return render_template(
        "waiting_access.html",
        email=email
    )

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
    update_data("SmartHome/Salon/Actionneurs/Alarme", {"etat": False, "alerte": False})
    return "OK"

@app.route("/set_chauffage_seuil/<value>")
def set_chauffage_seuil(value):
    update_data("SmartHome/Chambre_1/Actionneurs/Chauffage", {
        "seuil": float(value)
    })
    return "OK"

@app.route("/toggle_chauffage_auto/<state>")
def toggle_chauffage_auto(state):

    update_data("SmartHome/Chambre_1/Actionneurs/Chauffage", {
        "mode_auto": state == "1"
    })
    return "OK"

@app.route("/set_ventilateur_seuil/<value>")
def set_ventilateur_seuil(value):
    update_data("SmartHome/Chambre_1/Actionneurs/Ventilateur", {
        "seuil": float(value)
    })
    return "OK"

@app.route("/toggle_ventilateur_auto/<state>")
def toggle_ventilateur_auto(state):

    update_data("SmartHome/Chambre_1/Actionneurs/Ventilateur", {
        "mode_auto": state == "1"
    })
    return "OK"

@app.route("/set_garage_seuil/<value>")
def set_garage_seuil(value):

    update_data("SmartHome/Garage/Actionneurs/LedStationnement", {
        "distance_activation": int(value)
    })

    return "OK"


#Historique
@app.route("/api/history/<room>/<sensor>/<metric>")
def history(room, sensor, metric):

    path = f"SmartHome/{room}/Capteurs/{sensor}/Historique/{metric}"
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

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        now = time.time()

        # Création entrée si absente
        if email not in login_attempts:
            login_attempts[email] = {
                "count": 0,
                "blocked_until": 0
            }

        user_attempt = login_attempts[email]

        # Vérifie si bloqué
        if now < user_attempt["blocked_until"]:

            remaining = int(user_attempt["blocked_until"] - now)

            error = (
                f"Trop de tentatives. "
                f"Réessayez dans {remaining} secondes."
            )

            return render_template(
                "login.html",
                error=error
            )

        user = login_user(email, password)

        if user:

            # Reset compteur
            login_attempts[email] = {
                "count": 0,
                "blocked_until": 0
            }

            session["user"] = email
            return redirect("/")

        # Mauvais login
        user_attempt["count"] += 1

        # Blocage après 5 essais
        if user_attempt["count"] >= 5:

            user_attempt["blocked_until"] = now + 30

            error = (
                "Trop de tentatives échouées. "
                "Compte bloqué 30 secondes."
            )

        else:

            remaining = 5 - user_attempt["count"]

            error = (
                f"Email ou mot de passe incorrect. "
                f"Essais restants : {remaining}"
            )

    return render_template(
        "login.html",
        error=error
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    error = None
    success = None

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Vérification mot de passe minimal
        if len(password) < 6:

            error = (
                "Le mot de passe doit contenir "
                "au moins 6 caractères."
            )

            return render_template(
                "register.html",
                error=error
            )

        user = register_user(email, password)

        if user:

            success = (
                "Compte créé avec succès. "
                "Vous pouvez maintenant vous connecter."
            )

            return render_template(
                "register.html",
                success=success
            )

        error = (
            "Cette adresse email est déjà utilisée."
        )

    return render_template(
        "register.html",
        error=error,
        success=success
    )


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


def run_flask():
    app.run(host='0.0.0.0', port=5000)
    #http://127.0.0.1:5000/
    #