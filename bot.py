import os
from flask import Flask, request
from binance.client import Client
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key, api_secret)

telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

leverage = int(os.getenv("LEVERAGE", 2))
entry_usdt = float(os.getenv("ENTRY_USDT", 5))

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": telegram_chat_id, "text": message}
    requests.post(url, data=payload)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data.get("ticker")
    if not symbol:
        return {"error": "No ticker provided"}, 400

    try:
        mark_price_data = client.futures_mark_price(symbol=symbol)
        mark_price = float(mark_price_data["markPrice"])
        quantity = round(entry_usdt / mark_price, 3)

        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        client.futures_create_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=quantity
        )
        send_telegram_message(f"🚀 Ordem executada com sucesso para {symbol} com quantidade {quantity}")
        return {"status": "executed"}
    except Exception as e:
        send_telegram_message(f"❌ Erro ao executar ordem para {symbol}: {str(e)}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
