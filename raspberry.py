import serial
import time

from firebase_control import get_data
from firebase_control import update_data

arduino = serial.Serial('/dev/ttyACM0', 9600)

time.sleep(2)

last_states = {}

actionneurs = {
    "SmartHome/Salon/Actionneurs/Eclairage": {
        "on": b'S',
        "off": b's'
    },

    "SmartHome/Salon/Actionneurs/Alarme": {
        "on": b'A',
        "off": b'a'
    },

    "SmartHome/Chambre_1/Actionneurs/Eclairage": {
        "on": b'L',
        "off": b'l'
    },

    "SmartHome/Chambre_1/Actionneurs/Chauffage": {
        "on": b'H',
        "off": b'h'
    },

    "SmartHome/Chambre_1/Actionneurs/Ventilateur": {
        "on": b'R',
        "off": b'r'
    },

    "SmartHome/Chambre_2/Actionneurs/Eclairage": {
        "on": b'K',
        "off": b'k'
    },

    "SmartHome/Chambre_2/Actionneurs/Chauffage": {
        "on": b'J',
        "off": b'j'
    },

    "SmartHome/Garage/Actionneurs/LedStationnement": {
        "on": b'P',
        "off": b'p'
    }
}


def run_raspberry():
    while True:

        try:

            data = arduino.readline().decode().strip()

            parts = data.split(";")

            for p in parts:

                #Salon
                if p.startswith("S:"):

                    vals = p[2:].split(",")

                    update_data(
                        "SmartHome/Salon/Capteurs/DHT11",
                        {
                            "temperature": float(vals[0]),
                            "humidite": float(vals[1])
                        }
                    )

                #Chambre 1
                elif p.startswith("C:"):

                    vals = p[2:].split(",")

                    update_data(
                        "SmartHome/Chambre_1/Capteurs/DHT22",
                        {
                            "temperature": float(vals[0]),
                            "humidite": float(vals[1])
                        }
                    )

                #Chambre 2
                elif p.startswith("N:"):

                    update_data(
                        "SmartHome/Chambre_2/Capteurs/NiveauSonore",
                        {
                            "niveau": int(p[2:])
                        }
                    )

                #Garage
                elif p.startswith("G:"):

                    update_data(
                        "SmartHome/Garage/Capteurs/Ultrason",
                        {
                            "distance": int(p[2:])
                        }
                    )

        except Exception as e:

            print("Erreur lecture :", e)

        #Firebase -> Arduino

        for chemin_actionneur, commandes in actionneurs.items():

            try:

                chemin_etat = chemin_actionneur + "/etat"

                etat = get_data(chemin_etat)

                # Si changement
                if last_states.get(chemin_actionneur) != etat:

                    if etat:

                        arduino.write(commandes["on"])

                        print(
                            f"{chemin_actionneur} -> ON"
                        )

                    else:

                        arduino.write(commandes["off"])

                        print(
                            f"{chemin_actionneur} -> OFF"
                        )

                    # Sauvegarde dernier état
                    last_states[chemin_actionneur] = etat

            except Exception as e:

                print(
                    f"Erreur actionneur {chemin_actionneur} :",
                    e
                )

        #Seuils

        distance = get_data(
            "SmartHome/Garage/Capteurs/Ultrason/distance"
        )

        distance_activation = get_data(
            "SmartHome/Garage/Actionneurs/LedStationnement/distance_activation"
        )

        if distance <= distance_activation:

            update_data(
                "SmartHome/Garage/Actionneurs/LedStationnement",
                {
                    "etat": True
                }
            )

        else:

            update_data(
                "SmartHome/Garage/Actionneurs/LedStationnement",
                {
                    "etat": False
                }
            )

        time.sleep(0.2)