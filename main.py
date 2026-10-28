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
        return mcap, price, vol, liq
    except:
        return 66, 0.0000000694, 148, 34

def get_font(size, bold=False):
    for name in ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except:
            continue
    return ImageFont.load_default()

def make_card():
    W, H = 1024, 700
    mcap, price, vol, liq = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 0.0

    # Bullish logic
    if gain >= 10:
        bg_color, border_color, title_color = "#0A1F0A", "#00FF00", "#00FF00"
        emoji, hype_text, mode = "🚀🔥", "MEGA PUMP!!!", "MEGA BULLISH"
    elif gain >= 5:
        bg_color, border_color, title_color = "#0A1414", "#00FF88", "#00FF88"
        emoji, hype_text, mode = "🚀", "BULLISH AF!", "BULLISH"
    elif gain >= 1:
        bg_color, border_color, title_color = "#14140A", "#FFD700", "#FFD700"
        emoji, hype_text, mode = "📈", "PUMPING!", "PUMPING"
    else:
        bg_color, border_color, title_color = "#0A0A0A", "#00FF88", "#00FF88"
        emoji, hype_text, mode = "💎", "EARLY GEM!", "EARLY"

    img = Image.new('RGB', (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=30, outline=border_color, width=5)

    # Logo
    logo_size = 200
    logo_x, logo_y = W - logo_size - 30, 20
    try:
        if os.path.exists("logo.png"):
            logo = Image.open("logo.png").convert("RGBA")
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            mask = Image.new('L', (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size), fill=255)
            img.paste(logo, (logo_x, logo_y), mask)
            draw.ellipse([(logo_x-3, logo_y-3),(logo_x+logo_size+3, logo_y+logo_size+3)], outline=border_color, width=3)
    except Exception as e:
        print(f"Logo error: {e}")

    draw.text((30, 15), f"{emoji} $MEH {gain:.2f}x", fill=title_color, font=get_font(70, True))
    draw.text((30, 95), f"{hype_text} • {mode}", fill=title_color, font=get_font(22, True))
    draw.text((30, 125), "MEH / WBNB • BSC", fill="white", font=get_font(26, True))
    draw.text((30, 155), "AUTO EVERY 3 MIN", fill=border_color, font=get_font(16))

    draw.rounded_rectangle([(30, 210),(300, 300)], radius=12, fill="#111111")
    draw.text((50, 220), "MCap", fill="#AAAAAA", font=get_font(20))
    draw.text((50, 245), f"${mcap:,.0f}", fill=title_color, font=get_font(28, True))

    draw.rounded_rectangle([(330, 210),(600, 300)], radius=12, fill="#111111")
    draw.text((350, 220), "Vol 24h", fill="#AAAAAA", font=get_font(20))
    draw.text((350, 245), f"${vol:,.0f}", fill="white", font=get_font(28, True))

    draw.rounded_rectangle([(630, 210),(900, 300)], radius=12, fill="#111111")
    draw.text((650, 220), "Liq", fill="#AAAAAA", font=get_font(20))
    draw.text((650, 245), f"${liq:,.0f}", fill="white", font=get_font(28, True))

    draw.rounded_rectangle([(30, 320),(600, 410)], radius=12, fill="#111111")
    draw.text((50, 330), "Price", fill="#AAAAAA", font=get_font(20))
    draw.text((50, 355), f"${price:.10f}", fill="white", font=get_font(28, True))

    draw.text((30, 450), f"{emoji} {hype_text} {emoji}", fill=title_color, font=get_font(24, True))

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, mode, hype_text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE!\n\nCommands:\n/start - Start\n/mehcard - Show MEH Card")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol, mode, hype = make_card()
    if gain >= 10:
        caption = f"🚀🚀🚀 MEGA BULLISH!!! $MEH {gain:.2f}x 🚀🚀🚀\n🔥 {hype} - WE PUMPING HARD!\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n💎 EARLY STILL - LFG!!!\n\n{CA}"
    elif gain >= 5:
        caption = f"🚀 BULLISH AF! $MEH {gain:.2f}x 🚀\n📈 {hype} - KEEP PUMPING!\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n\n{CA}"
    else:
        caption = f"{'🚀' if gain >=1 else '💎'} $MEH {gain:.2f}x BSC! {hype}\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n💵 {price:.10f}\n\n{CA}\ndexscreener.com/bsc/{CA}"
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
