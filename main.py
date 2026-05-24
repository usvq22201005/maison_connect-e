import threading

from serveur_flask import run_flask
from historique import run_historique
from arduino import run_raspberry


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

raspberry_thread = threading.Thread(target=run_raspberry)

# =========================
# DAEMON
# =========================

flask_thread.daemon = True
history_thread.daemon = True
raspberry_thread.daemon = True

# =========================
# START
# =========================

flask_thread.start()
history_thread.start()
raspberry_thread.start()

# =========================
# KEEP ALIVE
# =========================

flask_thread.join()
history_thread.join()
raspberry_thread.join()