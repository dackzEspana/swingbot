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

#==== LIMPIAR SYMBOL ====

def limpiar_symbol(symbol):

    symbol = symbol.replace(".P", "")
    symbol = symbol.replace("USDT", "-USDT")

    return symbol

#==== FIN LIMPIAR SYMBOL ====


#==== OBTENER VELAS ====

def obtener_velas(symbol):

    url = "https://www.okx.com/api/v5/market/candles"

    params = {
        "instId": symbol,
        "bar": "15m",
        "limit": "50"
    }

    response = requests.get(url, params=params)

    data = response.json()["data"]

    df = pd.DataFrame(
        data,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "volCcy",
            "volCcyQuote",
            "confirm"
        ]
    )

    df = df.iloc[::-1]

    df["timestamp"] = pd.to_datetime(
        df["timestamp"].astype(float),
        unit="ms"
    )

    df.set_index("timestamp", inplace=True)

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    return df

#==== FIN OBTENER VELAS ====


#==== GENERAR GRAFICO ====

def generar_grafico(df):

    mc = mpf.make_marketcolors(
        up='#7CFC00',
        down='#FF3B30',
        edge='inherit',
        wick='inherit'
    )

    estilo = mpf.make_mpf_style(
        marketcolors=mc,
        facecolor='#050B16',
        figcolor='#050B16',
        gridcolor='#1A2233'
    )

    mpf.plot(
        df,
        type='candle',
        style=estilo,
        volume=False,
        axisoff=True,
        tight_layout=True,
        savefig=dict(
            fname="grafico.png",
            dpi=200,
            bbox_inches="tight",
            pad_inches=0
        )
    )

#==== FIN GENERAR GRAFICO ====


#==== CREAR IMAGEN ====

def crear_imagen(signal, symbol, price):

    if signal == "BUY":
        plantilla = Image.open("buy.png")

    else:
        plantilla = Image.open("sell.png")

    grafico = Image.open("grafico.png")

    # AJUSTAREMOS ESTAS MEDIDAS DESPUES
    grafico = grafico.resize((1320, 520))

    plantilla.paste(
        grafico,
        (30, 500)
    )

    plantilla.save("senal_final.png")

    return "senal_final.png"

#==== FIN CREAR IMAGEN ====


#==== ENVIAR DISCORD ====

def enviar_discord():

    with open("senal_final.png", "rb") as file:

        requests.post(
            DISCORD_WEBHOOK_URL,
            files={
                "file": file
            }
        )

#==== FIN ENVIAR DISCORD ====


#==== WEBHOOK ====

app = Flask(__name__)

@app.route("/")
def home():
    return "SwingBot Online"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    signal = data["signal"]
    symbol_tv = data["symbol"]
    price = data["price"]

    symbol_okx = limpiar_symbol(symbol_tv)

    df = obtener_velas(symbol_okx)

    generar_grafico(df)

    crear_imagen(
        signal,
        symbol_tv,
        price
    )

    enviar_discord()

    return jsonify({
        "status": "ok"
    })

#==== FIN WEBHOOK ====


#==== APP ====

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000
    )

#==== FIN APP ====
