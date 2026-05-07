import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

TELEGRAM_TOKEN = "8594771866:AAFoFLkM3Mk533L1MuY_0wnFGkSY51GsAL0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 MusicBot!\n\nQo'shiq nomini yozing!")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    await update.message.reply_text("🔍 Qidirmoqda...")
    try:
        subprocess.run([
            "yt-dlp",
            "--no-check-certificates",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "5",
            "-o", "/tmp/audio.mp3",
            f"ytsearch1:{q}"
        ], timeout=120, check=True)
        filepath = "/tmp/audio.mp3"
        if os.path.exists(filepath):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_AUDIO)
            with open(filepath, "rb") as f:
                await update.message.reply_audio(audio=f, title=q)
            os.remove(filepath)
        else:
            await update.message.reply_text("❌ Topilmadi. Boshqacha yozing.")
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
