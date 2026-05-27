import threading

from serveur_flask import run_flask
from historique import run_historique
from arduino import comm_arduino


# =========================
# THREAD FLASK
# =========================

flask_thread = threading.Thread(target=run_flask)

# =========================
# THREAD HISTORIQUE
# =========================

history_thread = threading.Thread(target=run_historique)

# =========================
# THREAD RASPBERRY
# =========================

arduino_thread = threading.Thread(target=comm_arduino)

# =========================
# DAEMON
# =========================

flask_thread.daemon = True
history_thread.daemon = True
arduino_thread.daemon = True

# =========================
# START
# =========================

flask_thread.start()
history_thread.start()
arduino_thread.start()

# =========================
# KEEP ALIVE
# =========================

flask_thread.join()
history_thread.join()
arduino_thread.join()