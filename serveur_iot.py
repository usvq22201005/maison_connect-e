from flask import Flask
import threading
import time

#Bool qui permet d'exécuter sans avoir l'Arduino de branché
arduino_present = False

if arduino_present:
    import serial
    arduino = serial.Serial('/dev/ttyACM0', 9600)
    time.sleep(2)

    temperature_salon = "..."
    humidity_salon = "..."

    temperature_chambre = "..."
    humidity_chambre = "..."

    sound_level = "..."
    garage_distance = "..."

    def read_serial():
        global temperature_salon, humidity_salon
        global temperature_chambre, humidity_chambre
        global sound_level, garage_distance

        while True:
            try:
                data = arduino.readline().decode().strip()
                parts = data.split(";")

                for p in parts:
                    if p.startswith("S:"):
                        vals = p[2:].split(",")
                        temperature_salon = vals[0]
                        humidity_salon = vals[1]

                    elif p.startswith("C:"):
                        vals = p[2:].split(",")
                        temperature_chambre = vals[0]
                        humidity_chambre = vals[1]

                    elif p.startswith("N:"):
                        sound_level = p[2:]

                    elif p.startswith("G:"):
                        garage_distance = p[2:]

            except:
                pass


    thread = threading.Thread(target=read_serial)
    thread.daemon = True
    thread.start()
else:
    arduino = None

    temperature_salon = "22"
    humidity_salon = "45"

    temperature_chambre = "20"
    humidity_chambre = "50"

    sound_level = "15"
    garage_distance = "30"

    app = Flask(__name__)



@app.route("/")
def home():
    status_garage = "🟢 Libre"

    try:
        if garage_distance != "..." and int(garage_distance) < 10:
            status_garage = "🚗 Voiture présente"
    except:
        pass

    return f"""
    <html>
    <body style="font-family:Arial">

    <h1>🏠 Smart Home</h1>

    <h2>🛋 Salon</h2>
    <p>Temp: {temperature_salon} °C</p>
    <p>Hum: {humidity_salon} %</p>

    <a href="/salon_on"><button>💡 ON</button></a>
    <a href="/salon_off"><button>OFF</button></a>

    <a href="/arm"><button>🚨 ARMER</button></a>
    <a href="/disarm"><button>DESARMER</button></a>

    <hr>

    <h2>🛏 Chambre 1</h2>
    <p>Temp: {temperature_chambre} °C</p>
    <p>Hum: {humidity_chambre} %</p>

    <a href="/led_on"><button>💡 ON</button></a>
    <a href="/led_off"><button>OFF</button></a>

    <a href="/heat_on"><button>🔥 ON</button></a>
    <a href="/heat_off"><button>OFF</button></a>

    <a href="/relay_on"><button>⚡ Relais ON</button></a>
    <a href="/relay_off"><button>OFF</button></a>

    <hr>

    <h2>🛏 Chambre 2</h2>
    <p>🎤 Niveau sonore : {sound_level}</p>

    <a href="/led2_on"><button>💡 ON</button></a>
    <a href="/led2_off"><button>OFF</button></a>

    <a href="/heat2_on"><button>🔥 ON</button></a>
    <a href="/heat2_off"><button>OFF</button></a>

    <hr>

    <h2>🚗 Garage</h2>
    <p>Distance : {garage_distance} cm</p>
    <p>{status_garage}</p>

    </body>
    </html>
    """

# ROUTES

#Fonction qui prend en entrée ce que l'on souhaite envoyer en série à l'arduino, affiche dans la console si l'arduino n'est pas branché
def send_command(commande):
    if arduino_present:
        arduino.write(commande)
    else:
        print("Commande envoyée : ", commande)

@app.route("/salon_on")
def salon_on():
    send_command(b'S')
    return "OK"

@app.route("/salon_off")
def salon_off():
    send_command(b's')
    return "OK"

@app.route("/led_on")
def led_on():
    send_command(b'L')
    return "OK"

@app.route("/led_off")
def led_off():
    send_command(b'l')
    return "OK"

@app.route("/heat_on")
def heat_on():
    send_command(b'H')
    return "OK"

@app.route("/heat_off")
def heat_off():
    send_command(b'h')
    return "OK"

@app.route("/relay_on")
def relay_on():
    send_command(b'R')
    return "OK"

@app.route("/relay_off")
def relay_off():
    send_command(b'r')
    return "OK"

@app.route("/led2_on")
def led2_on():
    send_command(b'K')
    return "OK"

@app.route("/led2_off")
def led2_off():
    send_command(b'k')
    return "OK"

@app.route("/heat2_on")
def heat2_on():
    send_command(b'J')
    return "OK"

@app.route("/heat2_off")
def heat2_off():
    send_command(b'j')
    return "OK"

@app.route("/arm")
def arm():
    send_command(b'A')
    return "OK"

@app.route("/disarm")
def disarm():
    send_command(b'a')
    return "OK"

app.run(host='0.0.0.0', port=5000)