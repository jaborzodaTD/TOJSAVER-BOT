import os
import re
import tempfile

import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
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
        "📥 Отправь ссылку на Instagram, YouTube или TikTok.\n\n"
        "После отправки выбери формат:"
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

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 Видео", callback_data="video"),
            InlineKeyboardButton("🎵 MP3", callback_data="audio"),
        ]
    ]

    await update.message.reply_text(
        "📥 Ссылка получена!\n\n"
        "Выбери формат:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text("❌ Ссылка потеряна. Отправь её ещё раз.")
        return

    if query.data == "video":
        await query.edit_message_text("⏳ Скачиваю видео...")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output = os.path.join(
                    temp_dir,
                    "%(title).80s.%(ext)s"
                )

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

                await query.edit_message_text("🎬 Видео готово!")

                with open(filename, "rb") as video:
                    await query.message.reply_video(
                        video=video,
                        caption="🎬 TOJSAVER"
                    )

        except Exception as e:
            print(f"Video error: {e}")

            await query.edit_message_text(
                "❌ Не удалось скачать видео."
            )

    elif query.data == "audio":
        await query.edit_message_text("⏳ Скачиваю музыку...")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output = os.path.join(
                    temp_dir,
                    "%(title).80s.%(ext)s"
                )

                options = {
                    "outtmpl": output,
                    "format": "bestaudio/best",
                    "noplaylist": True,
                    "quiet": True,
                    "no_warnings": True,
                    "restrictfilenames": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }

                with yt_dlp.YoutubeDL(options) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    filename = os.path.splitext(filename)[0] + ".mp3"

                if not os.path.exists(filename):
                    raise FileNotFoundError("MP3 не найден")

                await query.edit_message_text("🎵 Музыка готова!")

                with open(filename, "rb") as audio:
                    await query.message.reply_audio(
                        audio=audio,
                        caption="🎵 TOJSAVER"
                    )

        except Exception as e:
            print(f"Audio error: {e}")

            await query.edit_message_text(
                "❌ Не удалось скачать музыку."
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

    app.add_handler(
        CallbackQueryHandler(download_media)
    )

    print("TOJSAVER запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
