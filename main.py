import os, asyncio, threading, requests
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def get_live_data():
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{CA}"
        r = requests.get(url, timeout=10).json()
        if not r.get('pairs'): return 0, 0
        pair = r['pairs'][0]
        mcap = float(pair.get('fdv', 0) or pair.get('marketCap', 0))
        price = float(pair.get('priceUsd', 0))
        vol = float(pair.get('volume', {}).get('h24', 0))
        liq = float(pair.get('liquidity', {}).get('usd', 0))
        return mcap, price, vol, liq
    except:
        return 52, 0.0000000548, 146, 31

def make_card():
    W, H = 1000, 650
    img = Image.new('RGB', (W, H), '#0F0F0F')
    draw = ImageDraw.Draw(img)
    mcap, price, vol, liq = get_live_data()
    gain = mcap / 10000 if mcap > 1000 else 0.0
    try:
        f_big = ImageFont.truetype("arialbd.ttf", 75)
        f_med = ImageFont.truetype("arial.ttf", 28)
        f_small = ImageFont.truetype("arial.ttf", 24)
    except:
        f_big = f_med = f_small = ImageFont.load_default()
    
    draw.rounded_rectangle([(0,0),(W,H)], radius=25, fill="#0F0F0F", outline="#00FF8A", width=4)
    draw.text((40, 30), f"$MEH {gain:.2f}x", fill="#00FF8A", font=f_big)
    draw.text((40, 135), "MEH / WBNB • BSC", fill="#FFFFFF", font=f_med)
    draw.text((40, 175), "AUTO EVERY 3 MIN", fill="#00FF8A", font=f_small)
    
    draw.text((40, 250), f"MCap\n${mcap:,.0f}", fill="white", font=f_med)
    draw.text((350, 250), f"Vol 24h\n${vol:,.0f}", fill="white", font=f_med)
    draw.text((40, 350), f"Price\n${price:.11f}", fill="white", font=f_med)
    draw.text((350, 350), f"Liq\n${liq:,.0f}", fill="white", font=f_med)
    
    path = "/tmp/meh.png"
    img.save(path)
    return path, gain, mcap, price, vol

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE!\n\nCommands:\n/start - Start\n/mehcard - Show MEH Card")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BSC! AUTO 3MIN\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n{price:.11f}\n\n{CA}\ndexscreener.com/bsc/{CA}"
    await update.message.reply_photo(photo=open(path, 'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    print("BOT LIVE - POLLING STARTED")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
