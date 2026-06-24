from flask import Flask, request, jsonify, send_file
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from PIL import Image, ImageDraw, ImageFont
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# =========================================
# APP
# =========================================

app = Flask(__name__)

# =========================================
# CONFIG
# =========================================


#==== CONEXIONES ====

WEBHOOK_TOKEN = "Dackz_Signals_X9pL2"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1515092627865731072/w2UXvtDWEyacRTUGFiXfArzo-q-YJ2Zp3oT_RWS7cdfFcVENHDcTRO97rBFuDOenYxre"

#==== FIN CONEXIONES ====

# =========================================
# OBTENER VELAS OKX
# =========================================
def obtener_velas(symbol):

    symbol_okx = symbol.replace("USDT", "-USDT")

    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol_okx}&bar=15m&limit=50"

    response = requests.get(url)

    data = response.json()

    velas = data["data"]

    velas.reverse()

    df = pd.DataFrame(
        velas,
        columns=[
            "timestamp",
            "Open",
            "High",
            "Low",
            "Close",
            "volume",
            "vol2",
            "vol3",
            "confirm",
        ],
    )

    df["Open"] = df["Open"].astype(float)
    df["High"] = df["High"].astype(float)
    df["Low"] = df["Low"].astype(float)
    df["Close"] = df["Close"].astype(float)

   
    df.index = pd.date_range(
        start="2024-01-01",
        periods=len(df),
        freq="min"
    )

    return df

# =========================================
# CREAR GRAFICO
# =========================================

def crear_grafico(df, tipo):

    datos = df.tail(50).copy()

    mc = mpf.make_marketcolors(
        up="#00ff00",
        down="#ff0000",
        wick="inherit",
        edge="inherit",
        volume="inherit"
    )

    estilo = mpf.make_mpf_style(
        marketcolors=mc,
        facecolor="none",
        figcolor="none",
        gridcolor="#111"
    )

    archivo = f"grafico_{tipo}.png"

    fig, ax = mpf.plot(
        datos,
        type="candle",
        style=estilo,
        figsize=(8, 5),
        returnfig=True,
        axisoff=False,
        tight_layout=True,
    )

    # =====================================
    # LINEA PRECIO
    # =====================================

    precio_actual = datos["Close"].iloc[-1]

    color_linea = "#39ff14" if tipo == "BUY" else "#ff3131"

    ax[0].plot(
        [len(datos)-1, len(datos)+4],
        [precio_actual, precio_actual],
        color=color_linea,
        linestyle="--",
        linewidth=1.2,
    )

    ax[0].text(
        len(datos)+4.5,
        precio_actual,
        f"{precio_actual:.2f}",
        color=color_linea,
        fontsize=11,
        va="center",
        ha="left",
        bbox=dict(
            facecolor="black",
            edgecolor=color_linea,
            boxstyle="round,pad=0.25"
        ),
    )

    fig.savefig(
        archivo,
        bbox_inches="tight",
        pad_inches=0,
        dpi=100,
        transparent=True
    )

    plt.close(fig)

    return archivo

# =========================================
# CREAR IMAGEN
# =========================================
def crear_imagen(tipo, symbol, precio, df):

    if tipo == "BUY":

        fondo = Image.open("Señal_Compra.png")

        color = "#39ff14"

    else:

        fondo = Image.open("Señal_Venta.png")

        color = "#ff3131"

    draw = ImageDraw.Draw(fondo)

    font_mediana = ImageFont.truetype(
        "BOOKOS.TTF",
        35
    )

    # =====================================
    # PAR
    # =====================================

    draw.text(
        (60, 550),
        symbol,
        fill="white",
        font=ImageFont.truetype(
            "comicbd.ttf",
            33
        ),
    )

    # =====================================
    # TEMPORALIDAD
    # =====================================

    #draw.text(
        #(200, 300),
        #interval,
        #fill="white",
        #font=ImageFont.truetype(
            #"BOOKOS.ttf",
           # 26
       # ),
    #)

    # =====================================
    # PRECIO
    # =====================================

    draw.text(
        (750, 550),
        f"{round(precio, 2)}",
        fill=color,
        font=ImageFont.truetype(
            "comicbd.ttf",
            33
        ),
   )

    # =====================================
    # EMA200
    # =====================================

    #draw.text(
        #(45, 350),
        #f"{round(ema200, 2)}",
        #fill=color,
        #font=font_mediana
    #)

    # =====================================
    # HORA
    # =====================================

    hora = (datetime.utcnow() - timedelta(hours=6)).strftime("%H:%M:%S")

    draw.text(
        (500, 1150),
        hora,
        fill="white",
        font=ImageFont.truetype(
            "BOOKOS.TTF",
            18
        ),
    )
    

    # =====================================
    # FUERZA
    # =====================================

    #draw.text(
         #(670, 700),
        # "ALTA",
         #fill=color,
        # font=ImageFont.truetype(
          #   "BOOKOS.TTF",
         #    20
        # ),
   #  )

    # =====================================
    # GRAFICO
    # =====================================

    chart = Image.open(crear_grafico(df, tipo))
    chart = chart.resize((820, 320))

    
    if tipo == "BUY":
    
        fondo.paste(chart, (35, 700))
        
        qr = Image.open("QR.jpg")
        
        qr = qr.resize((150, 170))
        
        fondo.paste(qr, (780, 1230))
        
        fecha = datetime.now().strftime("%d/%m/%Y")
        
        draw.text((160, 1150), fecha, fill="white", font=ImageFont.truetype("BOOKOS.TTF", 18), )
    else:
    
        fondo.paste(chart, (35, 700))
        
        qr = Image.open("QR.jpg")
        
        qr = qr.resize((150, 170))
        
        fondo.paste(qr, (780, 1230))
        
        fecha = datetime.now().strftime("%d/%m/%Y")
        
        draw.text((160, 1150), fecha, fill="white", font=ImageFont.truetype("BOOKOS.TTF", 18), )
    
   
    archivo = f"{tipo}.png"
    fondo.save(archivo)
    
    return archivo


# =========================================
# DISCORD
# =========================================

def enviar_discord(imagen):

    with open(imagen, "rb") as f:

        requests.post(
            DISCORD_WEBHOOK,
            files={
                "file": f
            },
        )


# =========================================
# WEBHOOK
# =========================================

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.get_json()

        print("===================================")
        print("ALERTA RECIBIDA")
        print(data)
        print("===================================")

        symbol = data.get("symbol", "BTCUSDT")
        tipo = data.get("signal", "BUY")
        precio = float(data.get("price", 0))

        print(f"TIPO: {tipo}")
        print(f"SYMBOL: {symbol}")
        print(f"PRECIO: {precio}")

        # ============================
        # OBTENER VELAS
        # ============================

        df = obtener_velas(symbol)

        # ============================
        # CREAR IMAGEN
        # ============================

        imagen = crear_imagen(
            tipo,
            symbol,
            precio,
            df
        )

        # ============================
        # ENVIAR DISCORD
        # ============================

        enviar_discord(imagen)

        return jsonify({
            "ok": True,
            "tipo": tipo,
            "symbol": symbol,
            "precio": precio
        })

    except Exception as e:

        print("ERROR WEBHOOK:")
        print(str(e))

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

# =========================================
# FIN WEBHOOK
# =========================================


# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return "BOT ACTIVO 🔥"

# =========================================
# HEALTH
# =========================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })

# =========================================

# START

# =========================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )


