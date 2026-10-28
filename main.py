import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update

# FIX PARA SA RENDER - magbubukas ng port
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Vip Bot LIVE!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# BOT CODE
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CA = "0x39db5438317e583d46123f4b114fef376872e00d"

async def start(update: Update, context):
    await update.message.reply_text(f"✅ MEH Bot LIVE na!\nCA: {CA}\n/mehcard")

async def mehcard(update: Update, context):
    await update.message.reply_text("✅ MEH card system ready boss! Gamit na yung bagong design.")

print("MEH BOT LIVE - with port binding")
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mehcard", mehcard))
app.run_polling()
