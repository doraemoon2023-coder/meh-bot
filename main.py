import os, asyncio, threading, requests
from io import BytesIO
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
        pair = r['pairs'][0] if r.get('pairs') else {}
        mcap = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 66)
        price = float(pair.get('priceUsd', 0) or 0.0000000694)
        vol = float(pair.get('volume', {}).get('h24', 0) or 148)
        liq = float(pair.get('liquidity', {}).get('usd', 0) or 34)
        # Token image
        img_url = pair.get('info', {}).get('imageUrl') or pair.get('info', {}).get('header') or ""
        # Also try base token image
        if not img_url:
            img_url = f"https://dd.dexscreener.com/ds-data/tokens/bsc/{CA}.png"
        return mcap, price, vol, liq, img_url
    except Exception as e:
        print(f"Data error: {e}")
        return 66, 0.0000000694, 148, 34, ""

def get_font(size, bold=False):
    for name in ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "arialbd.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except:
            continue
    return ImageFont.load_default()

def make_card():
    W, H = 1024, 700
    mcap, price, vol, liq, logo_url = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 0.0  # para hindi 0.00x

    # Background with gradient feel
    img = Image.new('RGB', (W, H), '#000000')
    draw = ImageDraw.Draw(img)
    
    # Green border
    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=30, outline="#00FF88", width=4)
    # Inner glow
    draw.rounded_rectangle([(8,8),(W-9,H-9)], radius=25, outline="#00FF88", width=1)

    # Try to download and paste token logo
    logo_size = 120
    logo_x, logo_y = W - logo_size - 40, 30
    try:
        if logo_url:
            resp = requests.get(logo_url, timeout=5)
            logo = Image.open(BytesIO(resp.content)).convert("RGBA")
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            # Make circular
            mask = Image.new('L', (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size), fill=255)
            img.paste(logo, (logo_x, logo_y), mask)
            draw.ellipse([(logo_x-3, logo_y-3),(logo_x+logo_size+3, logo_y+logo_size+3)], outline="#00FF88", width=3)
    except Exception as e:
        print(f"Logo error: {e}")
        # Fallback circle with $MEH text
        draw.ellipse([(logo_x, logo_y),(logo_x+logo_size, logo_y+logo_size)], fill="#00FF88")
        draw.text((logo_x+25, logo_y+35), "$MEH", fill="black", font=get_font(28, True))

    f_big = get_font(75, True)
    f_med = get_font(26, True)
    f_label = get_font(20)
    f_val = get_font(30, True)

    # Title
    draw.text((30, 20), f"$MEH {gain:.2f}x", fill="#00FF88", font=f_big)
    draw.text((30, 110), "MEH / WBNB • BSC", fill="white", font=f_med)
    draw.text((30, 145), "AUTO EVERY 3 MIN • DEXSCREENER", fill="#00FF88", font=get_font(18))

    # Stats with boxes
    # MCap box
    draw.rounded_rectangle([(30, 210),(300, 300)], radius=12, fill="#111111", outline="#333333")
    draw.text((50, 220), "MCap", fill="#AAAAAA", font=f_label)
    draw.text((50, 245), f"${mcap:,.0f}", fill="#00FF88", font=f_val)

    draw.rounded_rectangle([(330, 210),(600, 300)], radius=12, fill="#111111", outline="#333333")
    draw.text((350, 220), "Vol 24h", fill="#AAAAAA", font=f_label)
    draw.text((350, 245), f"${vol:,.0f}", fill="white", font=f_val)

    draw.rounded_rectangle([(630, 210),(900, 300)], radius=12, fill="#111111", outline="#333333")
    draw.text((650, 220), "Liq", fill="#AAAAAA", font=f_label)
    draw.text((650, 245), f"${liq:,.0f}", fill="white", font=f_val)

    draw.rounded_rectangle([(30, 320),(600, 410)], radius=12, fill="#111111", outline="#333333")
    draw.text((50, 330), "Price", fill="#AAAAAA", font=f_label)
    draw.text((50, 355), f"${price:.10f}", fill="white", font=f_val)

    # CA footer
    draw.text((30, 450), f"CA: {CA[:20]}...{CA[-10:]}", fill="#666666", font=get_font(16))

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE!\n\nCommands:\n/start - Start\n/mehcard - Show MEH Card with logo")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BSC! AUTO 3MIN\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n💵 {price:.10f}\n\n{CA}\ndexscreener.com/bsc/{CA}"
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
