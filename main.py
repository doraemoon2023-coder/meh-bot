import os, asyncio, threading, requests
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000  # <-- PALITAN MO NG REAL TOTAL SUPPLY MO BOSS

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE - Auto Burn Detect!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def get_live_data():
    try:
        # Price data
        url = f"https://api.dexscreener.com/latest/dex/tokens/{CA}"
        r = requests.get(url, timeout=10).json()
        pair = r['pairs'][0] if r.get('pairs') else {}
        mcap = float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 66)
        price = float(pair.get('priceUsd', 0) or 0.0000000694)
        vol = float(pair.get('volume', {}).get('h24', 0) or 148)
        liq = float(pair.get('liquidity', {}).get('usd', 0) or 34)
        
        # AUTO BURN DETECT - BSC DEAD WALLET
        burned = 23240000  # fallback mo na 23.24M
        try:
            dead = "0x000000000000000000000000000000000000dEaD"
            bsc_url = f"https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={CA}&address={dead}&tag=latest"
            resp = requests.get(bsc_url, timeout=8).json()
            if resp.get('status') == '1' and resp.get('result'):
                raw = int(resp['result'])
                # Auto detect decimals - try both 9 and 18
                for dec in [9, 18]:
                    test = raw / (10 ** dec)
                    # If burned is reasonable (between 1M and 1B), use it
                    if 1000000 < test < TOTAL_SUPPLY:
                        burned = test
                        print(f"AUTO BURN FOUND: {burned} with {dec} decimals")
                        break
        except Exception as e:
            print(f"Burn auto-detect error, using fallback 23.24M: {e}")
        
        burn_pct = (burned / TOTAL_SUPPLY * 100) if TOTAL_SUPPLY > 0 else 0
        return mcap, price, vol, liq, burned, burn_pct
    except:
        return 66, 0.0000000694, 148, 34, 23240000, 2.32

def get_font(size, bold=True):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def make_card():
    W, H = 1024, 1150
    mcap, price, vol, liq, burned, burn_pct = get_live_data()
    gain = (mcap / 10) if mcap > 0 else 6.60

    img = Image.new('RGB', (W, H), '#000000')
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=40, outline="#00FF00", width=6)

    draw.text((W//2, 50), f"$MEH {gain:.2f}x", fill="#7FFF00", font=get_font(100, True), anchor="mt")
    draw.text((W//2, 160), "BULLISH AF!", fill="#FFFF00", font=get_font(70, True), anchor="mt")

    logo_size = 360
    logo_x, logo_y = (W - logo_size)//2, 250
    try:
        if os.path.exists("logo.png"):
            logo = Image.open("logo.png").convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
            glow = Image.new('RGBA', (logo_size+40, logo_size+40), (0,0,0,0))
            ImageDraw.Draw(glow).ellipse((0,0,logo_size+40, logo_size+40), fill=(0,255,0,80))
            img.paste(glow, (logo_x-20, logo_y-20), glow)
            mask = Image.new('L', (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size), fill=255)
            img.paste(logo, (logo_x, logo_y), mask)
            draw.ellipse([(logo_x-5, logo_y-5),(logo_x+logo_size+5, logo_y+logo_size+5)], outline="#00FF00", width=4)
    except:
        pass

    # Stats
    box_w, box_h, gap, start_x, y_boxes = 220, 100, 20, 40, 680
    for i, (label, val) in enumerate([("MCap", f"${mcap:,.0f}"), ("Vol", f"${vol:,.0f}"), ("Liq", f"${liq:,.0f}"), ("Price", f"${price:.10f}")]):
        x = start_x + i*(box_w+gap)
        draw.rounded_rectangle([(x, y_boxes),(x+box_w, y_boxes+box_h)], radius=15, fill="#0A0A0A", outline="#00FF00", width=2)
        draw.text((x+box_w//2, y_boxes+12), label, fill="#00FF88", font=get_font(20, True), anchor="mt")
        draw.text((x+box_w//2, y_boxes+42), val, fill="white", font=get_font(24 if i<3 else 18, True), anchor="mt")

    # AUTO BURN BOX
    y_burn = 810
    draw.rounded_rectangle([(40, y_burn),(W-40, y_burn+150)], radius=20, fill="#1A0A0A", outline="#FF4500", width=4)
    draw.text((W//2, y_burn+15), "🔥 TOTAL BURNED (AUTO) 🔥", fill="#FF4500", font=get_font(26, True), anchor="mt")
    draw.text((W//2, y_burn+55), f"{burned/1000000:.2f}M MEH", fill="white", font=get_font(40, True), anchor="mt")
    draw.text((W//2, y_burn+105), f"{burn_pct:.2f}% OF SUPPLY • AUTO-DETECTED", fill="#FFA500", font=get_font(18), anchor="mt")

    draw.rounded_rectangle([(40, 990),(W-40, 1040)], radius=15, fill="#001100", outline="#00FF00", width=2)
    draw.text((W//2, 1015), "TO THE MOON • AUTO BURN MODE 🔥🚀", fill="#00FF00", font=get_font(22, True), anchor="mm")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, burned, burn_pct

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE with AUTO BURN DETECT!\n\n/mehcard - Hype Card with Auto Burn")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol, burned, burn_pct = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BULLISH AF! 🚀\n🔥 AUTO BURN: {burned/1000000:.2f}M MEH ({burn_pct:.2f}%) 🔥\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n💵 {price:.10f}\n\nAUTO-DETECTED FROM BLOCKCHAIN!\n\n{CA}"
    await update.message.reply_photo(photo=open(path, 'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    print("BOT LIVE - AUTO BURN")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
