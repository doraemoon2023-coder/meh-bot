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
        pair = r['pairs'][0] if r.get('pairs') else {}
        mcap = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 66)
        price = float(pair.get('priceUsd', 0) or 0.0000000694)
        vol = float(pair.get('volume', {}).get('h24', 0) or 148)
        liq = float(pair.get('liquidity', {}).get('usd', 0) or 34)
        return mcap, price, vol, liq
    except:
        return 66, 0.0000000694, 148, 34

def get_font(size, bold=True):
    try:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()

def make_card():
    W, H = 1024, 1024
    mcap, price, vol, liq = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60

    # Hype background
    img = Image.new('RGB', (W, H), '#000000')
    draw = ImageDraw.Draw(img)

    # Outer neon glow
    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=40, outline="#00FF00", width=6)
    draw.rounded_rectangle([(10,10),(W-11,H-11)], radius=35, outline="#00FF00", width=2)
    draw.rounded_rectangle([(20,20),(W-21,H-21)], radius=30, outline="#003300", width=1)

    # Top Title - HUGE
    draw.text((W//2, 50), f"$MEH {gain:.2f}x", fill="#7FFF00", font=get_font(110, True), anchor="mt")
    draw.text((W//2, 180), "BULLISH AF!", fill="#FFFF00", font=get_font(75, True), anchor="mt")
    draw.text((W//2, 265), "🚀 🚀 🚀", fill="white", font=get_font(30), anchor="mt")

    # Central Logo - BIG
    logo_size = 420
    logo_x, logo_y = (W - logo_size)//2, 310
    try:
        if os.path.exists("logo.png"):
            logo = Image.open("logo.png").convert("RGBA")
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            # Green glow background
            glow = Image.new('RGBA', (logo_size+40, logo_size+40), (0,0,0,0))
            ImageDraw.Draw(glow).ellipse((0,0,logo_size+40, logo_size+40), fill=(0,255,0,80))
            img.paste(glow, (logo_x-20, logo_y-20), glow)
            mask = Image.new('L', (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size), fill=255)
            img.paste(logo, (logo_x, logo_y), mask)
            draw.ellipse([(logo_x-5, logo_y-5),(logo_x+logo_size+5, logo_y+logo_size+5)], outline="#00FF00", width=4)
    except Exception as e:
        print(f"Logo error: {e}")

    # Stats boxes - 4 at bottom
    box_w, box_h = 220, 110
    gap = 20
    start_x = 40
    y_boxes = 780
    
    boxes = [
        ("MCap", f"${mcap:,.0f}"),
        ("Vol", f"${vol:,.0f}"),
        ("Liq", f"${liq:,.0f}"),
        ("Price", f"${price:.10f}")
    ]
    
    for i, (label, val) in enumerate(boxes):
        x = start_x + i*(box_w+gap)
        draw.rounded_rectangle([(x, y_boxes),(x+box_w, y_boxes+box_h)], radius=15, fill="#0A0A0A", outline="#00FF00", width=2)
        draw.text((x+box_w//2, y_boxes+15), label, fill="#00FF88", font=get_font(22, True), anchor="mt")
        draw.text((x+box_w//2, y_boxes+45), val, fill="white", font=get_font(28 if i<3 else 20, True), anchor="mt")

    # Footer - TO THE MOON
    draw.rounded_rectangle([(40, 920),(W-40, 970)], radius=15, fill="#001100", outline="#00FF00", width=2)
    draw.text((W//2, 945), "TO THE MOON • MOON MODE ACTIVATED 🚀", fill="#00FF00", font=get_font(22, True), anchor="mm")
    draw.text((W//2, 1000), "DYOR • @MEHTOKEN • #MEH • NO SLEEP JUST COFFEE", fill="#666666", font=get_font(16), anchor="mt")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE!\n\n/mehcard - HYPE Card")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol = make_card()
    caption = f"🚀🚀🚀 $MEH {gain:.2f}x BULLISH AF! 🚀🚀🚀\n🔥 TO THE MOON - MOON MODE ACTIVATED!\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f} | Liq ${price*1000000000:,.0f}\n💎 {price:.10f}\n\n{CA}\n\n#MEH #BSC #BULLISH"
    await update.message.reply_photo(photo=open(path, 'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    print("BOT LIVE")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
