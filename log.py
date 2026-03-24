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

RUNNING = True
memory_logs=[]

def heartbeat():
    while RUNNING:
        n = 0
        memory_logs.append(f"{datetime.datetime.now()} - Heartbeat number {n}")
        if len(memory_logs) > 100:
            memory_logs.pop(0)
        time.sleep(60)

@app.route("/", methods=["GET", "POST"])
def index():
    price = None
    coin = None
    error = None
    smile = None

    if request.method == "POST":
        if request.form.get("coin"):
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

    logs = memory_logs[-100:]

    return render_template("index.html",price=price,coin=coin,error=error,logs=logs,smile=smile)
@app.route("/kill")
def kill():
    os.kill(os.getpid(), signal.SIGTERM)
    return "Killed"

if __name__ == "__main__":
    t = threading.Thread(target=heartbeat, daemon=True)
    t.start()
    app.run(port=2034, debug=False)