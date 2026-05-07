import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from groq import Groq

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

PROMPT = 'Return ONLY JSON: {"summary":"uzbek","results":[{"title":"","artist":"","spotify":"https://open.spotify.com/search/TITLE","youtube":"https://www.youtube.com/results?search_query=TITLE+ARTIST"}],"reels":[{"title":"","artist":"","trend":"uzbek","youtube":""}]}'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 MusicBot!\n\nQo'shiq yoki qo'shiqchi nomini yozing!")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": PROMPT + "\nSearch: " + q}],
            max_tokens=1000
        )
        raw = response.choices[0].message.content.strip()
        try:
            data = json.loads(raw)
            text = data.get("summary", "") + "\n\n"
            for i, s in enumerate(data.get("results", [])[:5], 1):
                text += f"{i}. {s.get('title','')} - {s.get('artist','')}\n"
            for i, r in enumerate(data.get("reels", [])[:3], 1):
                text += f"\n📱 {r.get('title','')} - {r.get('artist','')}\n{r.get('trend','')}\n"
            btns = []
            first = data.get("results", [{}])[0] if data.get("results") else {}
            row = []
            if first.get("spotify"):
                row.append(InlineKeyboardButton("🟢 Spotify", url=first["spotify"]))
            if first.get("youtube"):
                row.append(InlineKeyboardButton("🔴 YouTube", url=first["youtube"]))
            if row:
                btns.append(row)
            kb = InlineKeyboardMarkup(btns) if btns else None
            await update.message.reply_text(text or "Topilmadi", reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            await update.message.reply_text(raw[:3000])
    except Exception as e:
        await update.message.reply_text("Xato: " + str(e)[:200])

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    print("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
