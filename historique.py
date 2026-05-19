import time
from firebase_admin import db
from firebase_control import get_data, push_history


def cleanup_24h(path):

    ref = db.reference(path)
    data = ref.get()

    if not data:
        return

    now = int(time.time())

    for key, val in list(data.items()):

        if isinstance(val, dict) and "timestamp" in val:

            if now - val["timestamp"] > 86400:
                ref.child(key).delete()


while True:

    data = get_data("SmartHome")

    # =========================
    # SALON
    # =========================

    salon_temp = data["Salon"]["Capteurs"]["DHT11"]["temperature"]
    salon_hum = data["Salon"]["Capteurs"]["DHT11"]["humidite"]

    push_history(
        "SmartHome/Salon/Capteurs/DHT11/Historique/temperature",
        salon_temp
    )

    push_history(
        "SmartHome/Salon/Capteurs/DHT11/Historique/humidite",
        salon_hum
    )

    cleanup_24h(
        "SmartHome/Salon/Capteurs/DHT11/Historique/temperature"
    )

    cleanup_24h(
        "SmartHome/Salon/Capteurs/DHT11/Historique/humidite"
    )



    # =========================
    # CHAMBRE 1
    # =========================

    ch1_temp = data["Chambre_1"]["Capteurs"]["DHT22"]["temperature"]
    ch1_hum = data["Chambre_1"]["Capteurs"]["DHT22"]["humidite"]

    push_history(
        "SmartHome/Chambre_1/Capteurs/DHT22/Historique/temperature",
        ch1_temp
    )

    push_history(
        "SmartHome/Chambre_1/Capteurs/DHT22/Historique/humidite",
        ch1_hum
    )

    cleanup_24h(
        "SmartHome/Chambre_1/Capteurs/DHT22/Historique/temperature"
    )

    cleanup_24h(
        "SmartHome/Chambre_1/Capteurs/DHT22/Historique/humidite"
    )



    # =========================
    # CHAMBRE 2
    # =========================

    ch2_sound = data["Chambre_2"]["Capteurs"]["NiveauSonore"]["niveau"]

    push_history(
        "SmartHome/Chambre_2/Capteurs/NiveauSonore/Historique/niveau",
        ch2_sound
    )

    cleanup_24h(
        "SmartHome/Chambre_2/Capteurs/NiveauSonore/Historique/niveau"
    )



    # =========================
    # GARAGE
    # =========================

    garage_dist = data["Garage"]["Capteurs"]["Ultrason"]["distance"]

    push_history(
        "SmartHome/Garage/Capteurs/Ultrason/Historique/distance",
        garage_dist
    )

    cleanup_24h(
        "SmartHome/Garage/Capteurs/Ultrason/Historique/distance"
    )



    print("Historique mis à jour")

    time.sleep(60)