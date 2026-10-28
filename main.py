import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "MEH Bot LIVE!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ LIVE NA BOSS! /mehcard")

async def mehcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("$MEH 🚀 MCap $439k - Working!")

def run_bot():
    # FIX para sa event loop error
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mehcard", mehcard))
    print("BOT LIVE - POLLING STARTED")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # Flask sa background, Bot sa main - baliktad para gumana
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
