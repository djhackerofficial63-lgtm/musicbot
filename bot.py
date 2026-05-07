import os
import json
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from groq import Groq

TELEGRAM_TOKEN = "8594771866:AAFoFLkM3Mk533L1MuY_0wnFGkSY51GsAL0"
GROQ_API_KEY = "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"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 MusicBot!\n\nQo'shiq nomini yozing — men yuklab yuboraman!")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text("🔍 Qidirmoqda...")
    try:cmd = [
            "yt-dlp",
            f"ytsearch1:{q}",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "96K",
            "-o", "/tmp/%(title)s.%(ext)s",
            "--print", "after_move:filepath"
        
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        filepath = result.stdout.strip().split("\n")[-1]
        if filepath and os.path.exists(filepath):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_AUDIO)
            with open(filepath, "rb") as f:
                await update.message.reply_audio(audio=f, title=q)
            os.remove(filepath)
        else:
            await update.message.reply_text("❌ Qo'shiq topilmadi. Boshqacha yozing.")
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
