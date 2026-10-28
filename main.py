import os
import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# KUHA SA RENDER ENV VAR - WAG I-HARDCODE
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
    except Exception as e:
        print(f"API Error: {e}")
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
        f_small = ImageFont.truetype("arial.ttf", 28)
    except:
        f_big = f_med = f_small = ImageFont.load_default()

    draw.text((50, 40), "$MEH", fill="#00FF8A", font=f_big)
    draw.text((50, 170), f"{gain:.1f}x", fill="white", font=f_big)
    draw.text((50, 320), f"MCap: ${mcap:,.0f}", fill="white", font=f_med)
    draw.text((50, 370), f"Price: ${price}", fill="#888888", font=f_small)
    draw.text((50, 450), f"CA: {TOKEN_ADDRESS[:15]}...", fill="#555555", font=f_small)

    path = "/tmp/meh.png"
    img.save(path)
    return path, gain, mcap, price

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ MEH Vip Bot is LIVE!\n\n"
        "Commands:\n"
        "/start - I-start ang bot\n"
        "/mehcard - Ipakita ang card\n"
        "/help - Help"
    )
    print(f"New chat: {update.effective_chat.id}")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kumukuha ng live data...")
    path, gain, mcap, price = make_card()
    await update.message.reply_photo(
        photo=open(path, 'rb'), 
        caption=f"$MEH {gain:.1f}x | MCap ${mcap:,.0f} 🚀\nCA: {TOKEN_ADDRESS}"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("MEH Vip Bot running 24/7 via Render! Use /mehcard")

def main():
    print("BOT STARTING...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    app.add_handler(CommandHandler("help", help_cmd))
    print("MEH BOT LIVE - POLLING...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
