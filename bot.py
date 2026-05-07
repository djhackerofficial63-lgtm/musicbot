import os
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

TELEGRAM_TOKEN = "8594771866:AAFoFLkM3Mk533L1MuY_0wnFGkSY51GsAL0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 MusicBot!\n\nQo'shiq nomini yozing — 30 soniya preview yuboraman!")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    await update.message.reply_text("🔍 Qidirmoqda...")
    try:
        r = requests.get(f"https://api.deezer.com/search?q={q}&limit=1")
        data = r.json()
        if not data.get("data"):
            await update.message.reply_text("❌ Topilmadi. Boshqacha yozing.")
            return
        track = data["data"][0]
        title = track["title"]
        artist = track["artist"]["name"]
        preview = track["preview"]
        cover = track["album"]["cover_medium"]
        if not preview:
            await update.message.reply_text("❌ Preview yo'q.")
            return
        audio = requests.get(preview).content
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_AUDIO)
        await update.message.reply_audio(
            audio=audio,
            title=title,
            performer=artist,
            caption=f"🎵 {title} - {artist}\n⏱ 30 soniya preview"
        )
    except Exception as e:
        await update.message.reply_text("❌ Xato: " + str(e)[:200])

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    print("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
