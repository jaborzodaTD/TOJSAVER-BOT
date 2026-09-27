import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:instagram\.com|youtube\.com|youtu\.be|tiktok\.com)/\S+",
    re.IGNORECASE
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 TOJSAVER\n\n"
        "Отправь мне ссылку на видео:\n"
        "📥 Instagram\n"
        "📥 YouTube\n"
        "📥 TikTok\n\n"
        "Я обработаю её для тебя. 🚀"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if URL_PATTERN.search(text):
        await update.message.reply_text("⏳ Обрабатываю ссылку...")
    else:
        await update.message.reply_text(
            "🔗 Отправь корректную ссылку на Instagram, YouTube или TikTok."
        )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не найден")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("TOJSAVER запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
