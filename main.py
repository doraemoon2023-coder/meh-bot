import os, threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CA = "0x5c59232e53c47a812c80e5d99ccf924cee875070"

# KEEP ALIVE - PARA HINDI MAG EXIT EARLY
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "MEH BOT LIVE"
threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000))), daemon=True).start()

def make_card():
    W,H = 1000, 600
    img = Image.new("RGB", (W,H), "#0a1a10")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([5,5,W-5,H-5], radius=20, outline="#00ff88", width=3)
    try:
        f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        f2 = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
        f3 = ImageFont.truetype("DejaVuSans.ttf", 24)
    except:
        f1 = f2 = f3 = ImageFont.load_default()

    # TOP
    d.text((30,20), "MCap $1.5M | Vol $24K | Liq $57K | Burn 2.32%", fill="#00ff88", font=f3)
    # GITNA - BUY + BURN
    d.text((30,80), "BUY $MEH", fill="#00ff88", font=f1)
    d.text((30,150), "23.24M MEH", fill="white", font=f2)
    d.text((30,200), "Bought: $1,250", fill="white", font=f2)
    d.text((30,250), "Burn: 2.32% | Total Burn: 23.24M MEH", fill="#ff8a65", font=f3)
    # CA
    d.rounded_rectangle([20,320,980,390], radius=10, fill="#111")
    d.text((30,340), CA, fill="#888", font=f3)
    # BUYER
    d.text((30,420), "Buyer: 0x12ab...8f90", fill="#ccc", font=f3)
    d.text((30,460), "Holder since 3 days", fill="#ccc", font=f3)
    
    img.save("/tmp/meh.png")
    return "/tmp/meh.png"

async def start(update: Update, context):
    p = make_card()
    await update.message.reply_photo(photo=open(p,'rb'), caption="🚀 MEH BOT LIVE with BURN info!")

async def mehcard(update: Update, context):
    p = make_card()
    await update.message.reply_photo(photo=open(p,'rb'), caption="🚀 BUY $MEH | Burn 2.32% | $1,250")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mehcard", mehcard))

print("MEH BOT LIVE WITH PICTURE")
app.run_polling()
