import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are MusicBot. When user searches, return ONLY this JSON format:
{"summary":"info in Uzbek","results":[{"title":"","artist":"","album":"","year":"","genre":"","spotify":"https://open.spotify.com/search/TITLE","youtube":"https://www.youtube.com/results?search_query=TITLE+ARTIST","apple":"https://music.apple.com/search?term=TITLE"}],"reels":[{"title":"","artist":"","trend":"in Uzbek","spotify":"","youtube":""}]}
Return ONLY JSON."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 *MusicBot ga xush kelibsiz!*\n\nQo'shiq yoki qo'shiqchi nomini yozing!", parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Qo'shiq nomini yozing!\nMisol: Drake, Dilnoza, Blinding Lights")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": query}]
        )
        raw = message.content[0].text
        try:
            data = json.loads(raw.strip())
            text = ""
            if data.get("summary"):
                text += f"💬 {data['summary']}\n\n"
            results = data.get("results", [])
            if results:
                text += "🎵 *Qo'shiqlar:*\n"
                for i, s in enumerate(results[:5], 1):
                    text += f"\n*{i}. {s.get('title','')}*\n👤 {s.get('artist','')}\n"
                    if s.get('album'):
                        text += f"💿 {s['album']}\n"
            reels = data.get("reels", [])
            if reels:
                text += "\n📱 *Instagram Reels:*\n"
                for i, r in enumerate(reels[:3], 1):
                    text += f"\n*{i}. {r.get('title','')}*\n👤 {r.get('artist','')}\n"
                    if r.get('trend'):
                        text += f"📈 _{r['trend']}_\n"
            buttons = []
            first = results[0] if results else (reels[0] if reels else None)
            if first:
                row = []
                if first.get("spotify"):
                    row.append(InlineKeyboardButton("🟢 Spotify", url=first["spotify"]))
                if first.get("youtube"):
                    row.append(InlineKeyboardButton("🔴 YouTube", url=first["youtube"]))
                if row:
                    buttons.append(row)
            keyboard = InlineKeyboardMarkup(buttons) if buttons else None
            await update.message.reply_text(text or "Natija topilmadi", parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard, disable_web_page_preview=True)
        except:
            await update.message.reply_text(raw[:4000])
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {str(e)[:200]}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
