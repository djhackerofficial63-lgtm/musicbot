import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8594771866:AAFoFLkM3Mk533L1MuY_0wnFGkSY51GsAL0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 MusicBot!\n\nQo'shiq nomini yozing!")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    await update.message.reply_text("🔍 Qidirmoqda...")
    try:
        r = requests.get(f"https://api.deezer.com/search?q={q}&limit=10")
        data = r.json()
        if not data.get("data"):
            await update.message.reply_text("❌ Topilmadi.")
            return
        buttons = []
        for i, track in enumerate(data["data"]):
            title = track["title"]
            artist = track["artist"]["name"]
            duration = track["duration"]
            mins = duration // 60
            secs = duration % 60
            track_id = track["id"]
            buttons.append([InlineKeyboardButton(
                f"{i+1}. {title} - {artist} {mins}:{secs:02d}",
                callback_data=f"track_{track_id}"
            )])
        kb = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(f"🎵 '{q}' uchun natijalar:", reply_markup=kb)
    except Exception as e:
        await update.message.reply_text("❌ Xato: " + str(e)[:200])

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    track_id = query.data.replace("track_", "")
    await query.message.reply_text("⏳ Yuklanmoqda...")
    try:
        r = requests.get(f"https://api.deezer.com/track/{track_id}")
        track = r.json()
        title = track["title"]
        artist = track["artist"]["name"]
        album = track["album"]["title"]
        cover = track["album"]["cover_medium"]
        preview = track["preview"]
        if not preview:
            await query.message.reply_text("❌ Preview yo'q.")
            return
        audio = requests.get(preview, timeout=30).content
        await query.message.reply_photo(
            photo=cover,
            caption=f"🎵 *{title}*\n👤 {artist}\n💿 {album}\n⏱ 30 soniya preview",
            parse_mode="Markdown"
        )
        await query.message.reply_audio(
            audio=audio,
            title=title,
            performer=artist
        )
    except Exception as e:
        await query.message.reply_text("❌ Xato: " + str(e)[:200])

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
