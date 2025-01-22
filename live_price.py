#!/usr/bin/env python3
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    price = data['p']  # Prix du Bitcoin (string)
    print(f"Prix actuel du BTC/USDT : {price}")

def on_error(ws, error):
    print(f"Erreur : {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connexion fermée")

def on_open(ws):
    # S'abonner au flux BTC/USDT
    params = {
        "method": "SUBSCRIBE",
        "params": ["btcusdt@trade"],
        "id": 1
    }
    ws.send(json.dumps(params))

url = "wss://stream.binance.com:9443/ws"

ws = websocket.WebSocketApp(url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
