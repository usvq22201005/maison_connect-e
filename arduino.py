import serial
import time

from firebase_control import get_data, update_data, push_history
from historique import cleanup_24h

# Connexion à l'Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

last_states = {}
actionneurs = {
    "SmartHome/Salon/Actionneurs/Eclairage": {"on": b'S', "off": b's'},
    "SmartHome/Salon/Actionneurs/Alarme": {"on": b'A', "off": b'a'},
    "SmartHome/Chambre_1/Actionneurs/Eclairage": {"on": b'L', "off": b'l'},
    "SmartHome/Chambre_1/Actionneurs/Chauffage": {"on": b'H', "off": b'h'},
    "SmartHome/Chambre_1/Actionneurs/Ventilateur": {"on": b'R', "off": b'r'},
    "SmartHome/Chambre_2/Actionneurs/Eclairage": {"on": b'K', "off": b'k'},
    "SmartHome/Chambre_2/Actionneurs/Chauffage": {"on": b'J', "off": b'j'},
    "SmartHome/Garage/Actionneurs/LedStationnement": {"on": b'P', "off": b'p'}
}

def comm_arduino():
    last_seuil_garage = None
    sound_detected_this_minute = False
    last_minute = int(time.time() // 60)
    while True:
        # 1. LECTURE ARDUINO -> RASPBERRY
        try:
            # Si trop de lignes se sont accumulées dans le buffer série (embouteillage)
            if arduino.in_waiting > 500:
                arduino.reset_input_buffer() # On efface le retard pour repartir en temps réel
            
            if arduino.in_waiting > 0:
                data = arduino.readline().decode().strip()
                parts = data.split(";")
                for p in parts:
                    # Salon
                    if p.startswith("S:"):
                        vals = p[2:].split(",")
                        update_data("SmartHome/Salon/Capteurs/DHT11", {
                            "temperature": float(vals[0]),
                            "humidite": float(vals[1])
                        })
                    elif p.startswith("A:"):
                        val = int(p.split(":")[1])
                        update_data("SmartHome/Salon/Actionneurs/Alarme", {"alerte": val == 1})
                    # Chambre 1
                    elif p.startswith("C:"):
                        vals = p[2:].split(",")
                        update_data("SmartHome/Chambre_1/Capteurs/DHT22", {
                            "temperature": float(vals[0]),
                            "humidite": float(vals[1])
                        })
                    # Chambre 2
                    elif p.startswith("N:"):
                        try:
                            valeur = int(p[2:])
                        except ValueError:
                            continue

                        # On stocke uniquement un flag logique
                        if valeur == 1:
                            sound_detected_this_minute = True

                            # UI temps réel (optionnel mais propre)
                            update_data(
                                "SmartHome/Chambre_2/Capteurs/NiveauSonore",
                                {"niveau": 1}
                            )
                        else:
                            update_data(
                                "SmartHome/Chambre_2/Capteurs/NiveauSonore",
                                {"niveau": 0}
                            )
                    # Garage
                    elif p.startswith("G:"):
                        update_data("SmartHome/Garage/Capteurs/Ultrason", {"distance": int(p[2:])})
        except Exception as e:
            print("Erreur lecture Arduino :", e)

        # 2. RÉCUPÉRATION DE TOUTES LES DONNÉES DE FIREBASE (Une seule requête pour tout le cycle)
        try:
            db_snapshot = get_data("SmartHome")
            if not db_snapshot:
                time.sleep(0.5)
                continue
        except Exception as e:
            print("Erreur récupération Firebase :", e)
            time.sleep(0.5)
            continue

        # 3. LOGIQUE AUTOMATIQUE (CHAMBRE 1)
        try:
            ch1_actionneurs = db_snapshot.get("Chambre_1", {}).get("Actionneurs", {})
            ch1_capteurs = db_snapshot.get("Chambre_1", {}).get("Capteurs", {}).get("DHT22", {})
            temp_ch1 = ch1_capteurs.get("temperature")

            if temp_ch1 is not None:
                
                # ===== CHAUFFAGE AUTO =====
                chauffage_config = ch1_actionneurs.get("Chauffage", {})
                # Double vérification en temps réel pour éviter le conflit de snapshot
                if chauffage_config.get("mode_auto") is True:
                    # On revérifie rapidement Firebase en direct pour être SÛR que l'utilisateur n'a pas coupé le mode auto à l'instant
                    if get_data("SmartHome/Chambre_1/Actionneurs/Chauffage/mode_auto") is True:
                        seuil_heat = chauffage_config.get("seuil", 20)
                        nouvel_etat_heat = temp_ch1 < seuil_heat
                        if chauffage_config.get("etat") != nouvel_etat_heat:
                            update_data("SmartHome/Chambre_1/Actionneurs/Chauffage", {"etat": nouvel_etat_heat})
                            chauffage_config["etat"] = nouvel_etat_heat

                # ===== VENTILATEUR AUTO =====
                vent_config = ch1_actionneurs.get("Ventilateur", {})
                # Double vérification en temps réel pour éviter le conflit de snapshot
                if vent_config.get("mode_auto") is True:
                    # On revérifie rapidement Firebase en direct pour être SÛR que l'utilisateur n'a pas coupé le mode auto à l'instant
                    if get_data("SmartHome/Chambre_1/Actionneurs/Ventilateur/mode_auto") is True:
                        seuil_vent = vent_config.get("seuil", 25)
                        nouvel_etat_vent = temp_ch1 > seuil_vent
                        if vent_config.get("etat") != nouvel_etat_vent:
                            update_data("SmartHome/Chambre_1/Actionneurs/Ventilateur", {"etat": nouvel_etat_vent})
                            vent_config["etat"] = nouvel_etat_vent

        except Exception as e:
            print("Erreur dans la logique automatique Chambre 1 :", e)

        # 4. LOGIQUE AUTOMATIQUE (GARAGE)
        try:
            garage_data = db_snapshot.get("Garage", {})
            garage_act = garage_data.get("Actionneurs", {}).get("LedStationnement", {})
            new_seuil = garage_act.get("distance_activation", 0)

            # Envoi du seuil à l'Arduino si modifié
            if last_seuil_garage is None or new_seuil != last_seuil_garage:
                arduino.write(f"T{new_seuil}\n".encode())
                last_seuil_garage = new_seuil

            distance_garage = garage_data.get("Capteurs", {}).get("Ultrason", {}).get("distance", 999)
            etat_garage = distance_garage <= new_seuil
            if garage_act.get("etat") != etat_garage:
                update_data("SmartHome/Garage/Actionneurs/LedStationnement", {"etat": etat_garage})
                garage_act["etat"] = etat_garage
        except Exception as e:
            print("Erreur dans la logique Garage :", e)

        # 5. ENVOI DES ORDRES FIREBASE -> ARDUINO (Si l'état a changé)
        for chemin_actionneur, commandes in actionneurs.items():
            try:
                # Extraction de l'état depuis notre db_snapshot local
                parts = chemin_actionneur.split("/")  # ['SmartHome', 'Salon', 'Actionneurs', 'Eclairage']
                room = parts[1]
                act_name = parts[3]
                
                etat = db_snapshot.get(room, {}).get("Actionneurs", {}).get(act_name, {}).get("etat")

                if etat is None:
                    continue

                # Si l'état a changé par rapport au dernier état envoyé à l'Arduino
                if last_states.get(chemin_actionneur) != etat:
                    if etat:
                        arduino.write(commandes["on"])
                        print(f"{chemin_actionneur} -> ON")
                    else:
                        arduino.write(commandes["off"])
                        print(f"{chemin_actionneur} -> OFF")
                    
                    last_states[chemin_actionneur] = etat
            except Exception as e:
                print(f"Erreur envoi série pour {chemin_actionneur} :", e)

        # 6. GESTION DE L'HISTORIQUE DES CLAPS (Par minute)
        current_minute = int(time.time() // 60)

        if current_minute != last_minute:

            push_history(
                "SmartHome/Chambre_2/Capteurs/NiveauSonore/Historique/clap",
                1 if sound_detected_this_minute else 0
            )

            cleanup_24h(
                "SmartHome/Chambre_2/Capteurs/NiveauSonore/Historique/clap"
            )

            # reset logique
            sound_detected_this_minute = False
            last_minute = current_minute

        time.sleep(0.3)