from flask import Flask, request, jsonify, send_file
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from PIL import Image, ImageDraw, ImageFont
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

#==== CONEXIONES ====

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1515092627865731072/w2UXvtDWEyacRTUGFiXfArzo-q-YJ2Zp3oT_RWS7cdfFcVENHDcTRO97rBFuDOenYxre"

#==== FIN CONEXIONES ====


#====WEBHOOK====
app = Flask(__name__)

@app.route("/")
def home():
    return "SwingBot Online"

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    signal = data.get("signal", "N/A")
    symbol = data.get("symbol", "N/A")
    price = data.get("price", "N/A")

    mensaje = f"""
🚀 ABC SWING BOT

📈 Señal: {signal}
🪙 Par: {symbol}
💰 Precio: {price}
"""

    requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": mensaje}
    )

    print("========== ALERTA RECIBIDA ==========")
    print(data)
    print("=====================================")

    return jsonify({
        "status": "ok",
        "signal": signal,
        "symbol": symbol,
        "price": price
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

#====FIN WEBHOOK====
