import os
import threading
from flask import Flask
import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- PARA HINDI MAG FAILED SA RENDER ---
app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "MEH Bot is LIVE!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# --- BOT CODE ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("ERROR: WALANG TELEGRAM_BOT_TOKEN SA ENV!")
    exit(1)

TOKEN_ADDRESS = "0x39db5438317e583d46123f4b114fef376872e00d"

def get_live_data():
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{TOKEN_ADDRESS}"
        r = requests.get(url, timeout=10).json()
        pair = r['pairs'][0]
        mcap = float(pair.get('fdv', 0))
        price = float(pair.get('priceUsd', 0))
        return mcap, price
    except:
        return 439000, 0.00000439

def make_card():
    W, H = 1000, 600
    img = Image.new('RGB', (W, H), '#101E24')
    draw = ImageDraw.Draw(img)
    mcap, price = get_live_data()
    gain = mcap / 10000
    try:
        f_big = ImageFont.truetype("arialbd.ttf", 100)
        f_med = ImageFont.truetype("arial.ttf", 35)
    except:
        f_big = f_med = ImageFont.load_default()
    draw.text((50, 40), "$MEH", fill="#00FF8A", font=f_big)
    draw.text((50, 170), f"{gain:.1f}x", fill="white", font=f_big)
    draw.text((50, 320), f"MCap: ${mcap:,.0f}", fill="white", font=f_med)
    path = "/tmp/meh.png"
    img.save(path)
    return path, gain, mcap, price

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE!\n\nCommands:\n/start\n/mehcard\n/help")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kumukuha ng live data...")
    path, gain, mcap, price = make_card()
    await update.message.reply_photo(photo=open(path, 'rb'), caption=f"$MEH {gain:.1f}x | MCap ${mcap:,.0f} 🚀")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("MEH Vip Bot running 24/7!")

def main():
    # Start web server sa background para hindi mag timeout si Render
    threading.Thread(target=run_flask, daemon=True).start()
    print(f"Token OK: {TOKEN[:5]}... loaded")
    print("MEH BOT LIVE 3MIN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    app.add_handler(CommandHandler("help", help_cmd))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
