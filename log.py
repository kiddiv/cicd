from flask import Flask, render_template, request
import requests
import threading
import time
import datetime
import os
import signal
from prometheus_flask_exporter import PrometheusMetrics
app = Flask(__name__)

metrics = PrometheusMetrics(app)
LOG_FILE = "logs.txt"
RUNNING = True


def heartbeat():
    while RUNNING:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} HEARTBEAT OK\n")
        time.sleep(60)


@app.route("/", methods=["GET", "POST"])
def index():
    price = None
    coin = None
    error = None

    if request.method == "POST":
        coin = request.form["coin"].upper()
        url = f"https://api.coinbase.com/v2/exchange-rates?currency={coin}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            try:
                price = data["data"]["rates"]["USD"]
            except KeyError:
                error = "Нема"
        else:
            error = "Error API"
    elif "lol" in request.form:
        smile = '😎'
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()[-100:]

    return render_template("index.html",price=price,coin=coin,error=error,logs=logs,smile=smile)
@app.route("/kill")
def kill():
    os.kill(os.getpid(), signal.SIGTERM)
    return "Killed"

if __name__ == "__main__":
    t = threading.Thread(target=heartbeat, daemon=True)
    t.start()
    app.run(port=2034, debug=False)