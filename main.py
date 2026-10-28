import os, asyncio, threading, requests, random
from flask import Flask
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"
TOTAL_SUPPLY = 1000000000

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE - Fiery Burn!"

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
        burned = 23240000
        try:
            dead = "0x000000000000000000000000000000000000dEaD"
            bsc_url = f"https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={CA}&address={dead}&tag=latest"
            resp = requests.get(bsc_url, timeout=8).json()
            if resp.get('status') == '1' and resp.get('result'):
                raw = int(resp['result'])
                for dec in [9, 18]:
                    test = raw / (10 ** dec)
                    if 1000000 < test < TOTAL_SUPPLY:
                        burned = test
                        break
        except:
            pass
        burn_pct = (burned / TOTAL_SUPPLY * 100) if TOTAL_SUPPLY > 0 else 2.32
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
    
    for y in range(H):
        ratio = y / H
        g = int(15 + ratio * 10)
        draw.line([(0, y), (W, y)], fill=(0, g, 0))
    
    random.seed(123)
    for _ in range(100):
        x = random.randint(0, W)
        y = random.randint(0, 700)
        s = random.randint(2, 4)
        if random.random() > 0.5:
            draw.ellipse([(x, y),(x+s, y+s)], fill=(0, 255, 100))
        else:
            draw.ellipse([(x, y),(x+s, y+s)], fill=(255, 255, 255))

    for x in range(0, W, 80):
        draw.line([(x, 0),(x, H)], fill="#001a00", width=1)

    draw.rounded_rectangle([(0,0),(W-1,H-1)], radius=40, outline="#00FF00", width=6)
    draw.text((W//2, 50), f"$MEH {gain:.2f}x", fill="#7FFF00", font=get_font(100, True), anchor="mt")
    draw.text((W//2, 160), "BULLISH AF!", fill="#FFFF00", font=get_font(70, True), anchor="mt")

    logo_size = 360
    logo_x, logo_y = (W - logo_size)//2, 250
    try:
        if os.path.exists("logo.png"):
            logo = Image.open("logo.png").convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
            glow = Image.new('RGBA', (logo_size+60, logo_size+60), (0,0,0,0))
            ImageDraw.Draw(glow).ellipse((0,0,logo_size+60, logo_size+60), fill=(0,255,0,40))
            img.paste(glow, (logo_x-30, logo_y-30), glow)
            mask = Image.new('L', (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size), fill=255)
            img.paste(logo, (logo_x, logo_y), mask)
            draw.ellipse([(logo_x-5, logo_y-5),(logo_x+logo_size+5, logo_y+logo_size+5)], outline="#00FF00", width=4)
    except:
        pass

    box_w, box_h, gap, start_x, y_boxes = 220, 100, 20, 40, 680
    for i, (label, val) in enumerate([("MCap", f"${mcap:,.0f}"), ("Vol", f"${vol:,.0f}"), ("Liq", f"${liq:,.0f}"), ("Price", f"${price:.10f}")]):
        x = start_x + i*(box_w+gap)
        draw.rounded_rectangle([(x, y_boxes),(x+box_w, y_boxes+box_h)], radius=15, fill="#0A0A0A", outline="#00FF00", width=2)
        draw.text((x+box_w//2, y_boxes+12), label, fill="#00FF88", font=get_font(20, True), anchor="mt")
        draw.text((x+box_w//2, y_boxes+42), val, fill="white", font=get_font(24 if i<3 else 18, True), anchor="mt")

    # FIERY BURN BOX - 23.24M WITH FLAMES
    y_burn = 810
    burn_h = 160
    for i in range(12, 0, -2):
        glow_c = (60 + i*8, 15 + i*2, 0)
        draw.rounded_rectangle([(40-i, y_burn-i),(W-40+i, y_burn+burn_h+i)], radius=22+i, fill=glow_c)
    
    draw.rounded_rectangle([(40, y_burn),(W-40, y_burn+burn_h)], radius=20, fill="#1A0000", outline="#FF2200", width=4)
    
    flame_y = y_burn + burn_h - 20
    for x in range(60, W-60, 30):
        random.seed(x)
        h1 = random.randint(15, 30)
        h2 = random.randint(8, 20)
        draw.polygon([(x, flame_y), (x+15, flame_y-h1), (x+30, flame_y)], fill="#FF4500")
        draw.polygon([(x+5, flame_y), (x+15, flame_y-h2), (x+25, flame_y)], fill="#FFA500")
        draw.polygon([(x+10, flame_y), (x+15, flame_y-h2//2), (x+20, flame_y)], fill="#FFFF00")
    
    for y in [y_burn+25, y_burn+75, y_burn+115]:
        draw.polygon([(40, y), (55, y-10), (55, y+10)], fill="#FF4500")
        draw.polygon([(W-40, y), (W-55, y-10), (W-55, y+10)], fill="#FF4500")
    
    draw.text((W//2, y_burn+15), "🔥🔥 TOTAL BURNED (AUTO) 🔥🔥", fill="#FF2200", font=get_font(26, True), anchor="mt")
    draw.text((W//2+2, y_burn+57), f"{burned/1000000:.2f}M MEH", fill="#330000", font=get_font(42, True), anchor="mt")
    draw.text((W//2, y_burn+55), f"{burned/1000000:.2f}M MEH", fill="white", font=get_font(42, True), anchor="mt")
    draw.text((W//2, y_burn+105), f"{burn_pct:.2f}% OF SUPPLY • DEFLATIONARY 🔥", fill="#FFA500", font=get_font(18, True), anchor="mt")
    draw.text((W//2, y_burn+130), "♨️ BURN BABY BURN ♨️", fill="#FF6600", font=get_font(16, True), anchor="mt")

    draw.rounded_rectangle([(40, 990),(W-40, 1040)], radius=15, fill="#001100", outline="#00FF00", width=2)
    draw.text((W//2, 1015), "TO THE MOON • AUTO BURN MODE 🔥🚀", fill="#00FF00", font=get_font(22, True), anchor="mm")

    path = "/tmp/meh.png"
    img.save(path, quality=95)
    return path, gain, mcap, price, vol, burned, burn_pct

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MEH Vip Bot is LIVE!\n\n/mehcard - Fiery Burn Card")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path, gain, mcap, price, vol, burned, burn_pct = make_card()
    caption = f"🚀 $MEH {gain:.2f}x BULLISH AF! 🚀\n🔥 TOTAL BURNED: {burned/1000000:.2f}M MEH ({burn_pct:.2f}%) 🔥\n💰 MCap ${mcap:,.0f} | Vol ${vol:,.0f}\n\n{CA}"
    await update.message.reply_photo(photo=open(path, 'rb'), caption=caption)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    print("BOT LIVE - FIERY BURN")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
