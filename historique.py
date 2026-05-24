import time
from firebase_admin import db
from firebase_control import get_data, push_history


# =========================
# CLEANUP GLOBAL (24h)
# =========================

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


# =========================
# PUSH HISTORY AUTO
# =========================

def process_sensor(home_id, room, sensor_name, sensor_data):

    if not isinstance(sensor_data, dict):
        return

    historique_path = f"Homes/{home_id}/{room}/Capteurs/{sensor_name}/Historique"

    for key, value in sensor_data.items():

        # on ignore les sous-blocs type Historique
        if key == "Historique":
            continue

        # valeur simple capteur
        push_history(
            f"{historique_path}/{key}",
            value
        )

        cleanup_24h(f"{historique_path}/{key}")


# =========================
# MAIN LOOP
# =========================

def run_historique():

    while True:

        homes = get_data("Homes")

        if not homes:
            time.sleep(5)
            continue

        for home_id, home_data in homes.items():

            if not isinstance(home_data, dict):
                continue

            for room_name, room_data in home_data.items():

                if "Capteurs" not in room_data:
                    continue

                capteurs = room_data["Capteurs"]

                for sensor_name, sensor_data in capteurs.items():

                    process_sensor(
                        home_id,
                        room_name,
                        sensor_name,
                        sensor_data
                    )

        print("Historique mis à jour (auto multi-homes)")

        time.sleep(60)