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
        os.makedirs("/tmp/music", exist_ok=True)
        result = subprocess.run([
            "yt-dlp",
            "--no-check-certificates",
            "-f", "bestaudio/best",
            "-o", "/tmp/music/audio.%(ext)s",
            "--no-playlist",
            f"ytsearch1:{q}"
        ], timeout=120, capture_output=True, text=True)
        found = None
        for f in os.listdir("/tmp/music"):
            found = f"/tmp/music/{f}"
            break
        if found and os.path.exists(found):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_AUDIO)
            with open(found, "rb") as f:
                await update.message.reply_audio(audio=f, title=q)
            os.remove(found)
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
