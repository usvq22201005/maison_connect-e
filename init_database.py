from firebase_control import root

data = {
    "SmartHome" : {
        "Salon": {
            "Capteurs": {
                "DHT11": {
                    "temperature": 22,
                    "humidite": 40
                }
            },
            "Actionneurs": {
                "Eclairage": {
                    "etat": False
                },
                "Alarme": {
                    "etat": False
                }
            }
        },

        "Chambre_1": {
            "Capteurs": {
                "DHT22": {
                    "temperature": 20,
                    "humidite": 50
                }
            },
            "Actionneurs": {
                "Eclairage": {
                    "etat": False
                },
                "Chauffage": {
                    "etat": False,
                    "mode_auto": True,
                    "temperature_min": 20
                },
                "Ventilateur": {
                    "etat": False
                }
            }
        },

        "Chambre_2": {
            "Capteurs": {
                "NiveauSonore": {
                    "niveau": 15
                }
            },
            "Actionneurs": {
                "Eclairage": {
                    "etat": False
                },
                "Chauffage": {
                    "etat": True
                }
            }
        },

        "Garage": {
            "Capteurs": {
                "Ultrason": {
                    "distance": 90
                }
            },
            "Actionneurs": {
                "LedStationnement": {
                    "etat": True,
                    "distance_activation": 100
                }
            }
        }
    }
}

root.set(data)

print("Database initialisée !")