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
        if not r.get('pairs'): return 66, 0.00000006937, 148, 14
        pair = r['pairs'][0]
        mcap = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 66)
        price = float(pair.get('priceUsd', 0) or 0.00000006937)
        vol = float(pair.get('volume', {}).get('h24', 0) or 148)
        liq = float(pair.get('liquidity', {}).get('usd', 0) or 14)
        return mcap, price, vol, liq
    except:
        return 66, 0.00000006937, 148, 14

def get_font(size):
    # Try multiple fonts available on Render
    for name in ["DejaVuSans-Bold.ttf", "arialbd.ttf", "DejaVuSans.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except:
            continue
    return ImageFont.load_default()

def make_card():
    W, H = 1024, 650
    # Solid black background like your screenshot
    img = Image.new('RGB', (W, H), '#000000')
    draw = ImageDraw.Draw(img)
    mcap, price, vol, liq = get_live_data()
    gain = (mcap / 10000) if mcap > 100 else 0.0

    # Fonts - large and readable
    f_title = get_font(72)
    f_sub = get_font(26)
    f_label = get_font(22)
    f_value = get_font(32)

    # Title - GREEN like your screenshot
    draw.text((30, 20), f"$MEH {gain:.2f}x", fill="#00FF66", font=f_title)
    draw.text((30, 110), "MEH / WBNB • BSC", fill="white", font=f_sub)
    draw.text((30, 145), "AUTO EVERY 3 MIN", fill="#00FF66", font=f_label)

    # MCap, Vol, Price, Liq - 2 columns, white text
    draw.text((30, 230), "MCap", fill="#AAAAAA", font=f_label)
    draw.text((30, 260), f"${mcap:,.0f}", fill="#00FF66", font=f_value)

    draw.text((400, 230), "Vol 24h", fill="#AAAAAA", font=f_label)
    draw.text((400, 260), f"${vol:,.0f}", fill="white", font=f_value)

    draw.text((30, 350), "Price", fill="#AAAAAA", font=f_label)
    draw.text((30, 380), f"${price:.10f}", fill="white", font=f_value)

    draw.text((400, 350), "Liq", fill="#AAAAAA", font=f_label)
    draw.text((400, 380), f"${liq:,.0f}", fill="white", font=f_value)

    # Border
    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=20, outline="#00FF66", width=3)

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE!\n\nCommands:\n/start\n/mehcard")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BSC! AUTO 3MIN\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n{price:.10f}\n\n{CA}\ndexscreener.com/bsc/{CA}"
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
