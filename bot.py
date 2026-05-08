import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8594771866:AAFoFLkM3Mk533L1MuY_0wnFGkSY51GsAL0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 *MusicBot ga xush kelibsiz!*\n\n"
        "Qo'shiq yoki qo'shiqchi nomini yozing!\n\n"
        "Misol: Ummon, Shahlo Ahmedova, Drake",
        parse_mode="Markdown"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    await update.message.reply_text("🔍 Qidirmoqda...")
    try:
        r = requests.get(f"https://api.deezer.com/search?q={q}&limit=10", timeout=10)
        data = r.json()
        if not data.get("data"):
            await update.message.reply_text("❌ Topilmadi. Boshqacha yozing.")
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
                f"{i+1}. {title} - {artist} [{mins}:{secs:02d}]",
                callback_data=f"t_{track_id}"
            )])
        kb = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            f"🎵 *'{q}'* bo'yicha natijalar:\n\nQo'shiqni tanlang 👇",
            reply_markup=kb,
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text("❌ Xato: " + str(e)[:200])

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    track_id = query.data.replace("t_", "")
    msg = await query.message.reply_text("⏳ Yuklanmoqda...")
    try:
        r = requests.get(f"https://api.deezer.com/track/{track_id}", timeout=10)
        track = r.json()
        title = track["title"]
        artist = track["artist"]["name"]
        album = track["album"]["title"]
        cover = track["album"]["cover_xl"]
        preview = track["preview"]
        duration = track.get("duration", 0)
        mins = duration // 60
        secs = duration % 60
        if not preview:
            await msg.edit_text("❌ Bu qo'shiq uchun preview yo'q.")
            return
        audio_data = requests.get(preview, timeout=30).content
        await msg.delete()
        await query.message.reply_photo(
            photo=cover,
            caption=(
                f"🎵 *{title}*\n"
                f"👤 {artist}\n"
                f"💿 {album}\n"
                f"⏱ {mins}:{secs:02d}\n\n"
                f"_30 soniya preview_"
            ),
            parse_mode="Markdown"
        )
        await query.message.reply_audio(
            audio=audio_data,
            title=title,
            performer=artist,
            duration=30
        )
    except Exception as e:
        await msg.edit_text("❌ Xato: " + str(e)[:200])

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
