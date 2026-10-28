import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Web server para sa Render Web Service
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ LIVE NA BOSS! /mehcard")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("$MEH 🚀 MCap $439k")

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    print("BOT LIVE")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # Bot sa background thread, Flask sa main thread
    threading.Thread(target=run_bot, daemon=True).start()
    run_flask()
