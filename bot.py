import os
import re
import tempfile

import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:instagram\.com|youtube\.com|youtu\.be|tiktok\.com)/\S+",
    re.IGNORECASE,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 TOJSAVER\n\n"
        "Отправь мне ссылку на видео:\n"
        "📥 Instagram\n"
        "📥 YouTube\n"
        "📥 TikTok\n\n"
        "Я попробую скачать его для тебя. 🚀"
    )


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    match = URL_PATTERN.search(text)

    if not match:
        await update.message.reply_text(
            "🔗 Отправь корректную ссылку на Instagram, YouTube или TikTok."
        )
        return

    url = match.group(0)

    status = await update.message.reply_text("⏳ Обрабатываю ссылку...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            output = os.path.join(temp_dir, "%(title).80s.%(ext)s")

            options = {
                "outtmpl": output,
                "format": "best[ext=mp4]/best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "restrictfilenames": True,
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            if not os.path.exists(filename):
                files = os.listdir(temp_dir)

                if not files:
                    raise FileNotFoundError("Видео не найдено")

                filename = os.path.join(temp_dir, files[0])

            await status.edit_text("🎬 Видео готово!")

            with open(filename, "rb") as video:
                await update.message.reply_video(
                    video=video,
                    caption="🎬 TOJSAVER"
                )

    except Exception as e:
        print(f"Download error: {e}")

        await status.edit_text(
            "❌ Не удалось скачать видео.\n\n"
            "Возможно, ссылка недоступна или платформа требует авторизацию."
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не найден")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link
        )
    )

    print("TOJSAVER запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
