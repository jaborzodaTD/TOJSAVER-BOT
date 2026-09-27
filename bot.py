import os
import re
import tempfile

import yt_dlp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

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
    r"https?://(?:www\.)?"
    r"(?:instagram\.com|youtube\.com|youtu\.be|tiktok\.com)"
    r"/\S+",
    re.IGNORECASE,
)


TEXTS = {
    "ru": {
        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇷🇺 Видео и музыка из социальных сетей.\n\n"
            "📥 Отправь ссылку на Instagram, YouTube или TikTok."
        ),
        "menu": "🎬 <b>TOJSAVER</b>\n\nВыбери действие:",
        "choose_format": "📥 <b>Выбери формат:</b>",
        "video": "🎬 Видео",
        "audio": "🎵 MP3",
        "language": "🌐 Язык",
        "back": "⬅️ Назад",
        "processing_video": "⏳ Скачиваю видео...",
        "processing_audio": "⏳ Скачиваю музыку...",
        "video_ready": "🎬 Видео готово!",
        "audio_ready": "🎵 Музыка готова!",
        "error": "❌ Не удалось скачать файл.",
        "bad_link": "🔗 Отправь ссылку на Instagram, YouTube или TikTok.",
        "language_title": "🌐 <b>Выбери язык:</b>",
        "language_changed": "✅ Язык изменён.",
    },

    "tg": {
        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇹🇯 Видео ва мусиқиро аз шабакаҳои иҷтимоӣ зеркашӣ кун.\n\n"
            "📥 Линкаи Instagram, YouTube ё TikTok-ро фирист."
        ),
        "menu": "🎬 <b>TOJSAVER</b>\n\nАмалро интихоб кун:",
        "choose_format": "📥 <b>Форматро интихоб кун:</b>",
        "video": "🎬 Видео",
        "audio": "🎵 MP3",
        "language": "🌐 Забон",
        "back": "⬅️ Бозгашт",
        "processing_video": "⏳ Видео зеркашӣ шуда истодааст...",
        "processing_audio": "⏳ Мусиқӣ зеркашӣ шуда истодааст...",
        "video_ready": "🎬 Видео тайёр!",
        "audio_ready": "🎵 Мусиқӣ тайёр!",
        "error": "❌ Файлро зеркашӣ карда натавонистам.",
        "bad_link": "🔗 Линкаи Instagram, YouTube ё TikTok-ро фирист.",
        "language_title": "🌐 <b>Забонро интихоб кун:</b>",
        "language_changed": "✅ Забон иваз шуд.",
    },

    "en": {
        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇬🇧 Video and music downloader.\n\n"
            "📥 Send an Instagram, YouTube or TikTok link."
        ),
        "menu": "🎬 <b>TOJSAVER</b>\n\nChoose an action:",
        "choose_format": "📥 <b>Choose format:</b>",
        "video": "🎬 Video",
        "audio": "🎵 MP3",
        "language": "🌐 Language",
        "back": "⬅️ Back",
        "processing_video": "⏳ Downloading video...",
        "processing_audio": "⏳ Downloading music...",
        "video_ready": "🎬 Video ready!",
        "audio_ready": "🎵 Music ready!",
        "error": "❌ Failed to download the file.",
        "bad_link": "🔗 Send an Instagram, YouTube or TikTok link.",
        "language_title": "🌐 <b>Choose language:</b>",
        "language_changed": "✅ Language changed.",
    },
}


def get_lang(context):
    return context.user_data.get("lang", "ru")


def main_keyboard(lang):
    t = TEXTS[lang]

    keyboard = [
        [
            InlineKeyboardButton(t["video"], callback_data="menu_video"),
            InlineKeyboardButton(t["audio"], callback_data="menu_audio"),
        ],
        [
            InlineKeyboardButton(
                t["language"],
                callback_data="language"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def language_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="lang_tg"),
        ],
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    lang = get_lang(context)
    t = TEXTS[lang]

    await update.message.reply_text(
        t["welcome"],
        parse_mode="HTML",
        reply_markup=main_keyboard(lang),
    )


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    lang = get_lang(context)
    t = TEXTS[lang]

    text = update.message.text.strip()

    match = URL_PATTERN.search(text)

    if not match:
        await update.message.reply_text(t["bad_link"])
        return

    url = match.group(0)

    context.user_data["url"] = url

    await update.message.reply_text(
        t["choose_format"],
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    t["video"],
                    callback_data="video"
                ),
                InlineKeyboardButton(
                    t["audio"],
                    callback_data="audio"
                ),
            ],
            [
                InlineKeyboardButton(
                    t["language"],
                    callback_data="language"
                )
            ],
        ]),
    )


async def language_menu(update, context):

    query = update.callback_query
    await query.answer()

    lang = get_lang(context)
    t = TEXTS[lang]

    await query.edit_message_text(
        t["language_title"],
        parse_mode="HTML",
        reply_markup=language_keyboard(),
    )


async def change_language(update, context):

    query = update.callback_query
    await query.answer()

    lang = query.data.replace("lang_", "")

    context.user_data["lang"] = lang

    t = TEXTS[lang]

    await query.edit_message_text(
        t["language_changed"],
        reply_markup=main_keyboard(lang),
    )


async def download_media(update, context):

    query = update.callback_query
    await query.answer()

    lang = get_lang(context)
    t = TEXTS[lang]

    url = context.user_data.get("url")

    if not url:

        await query.edit_message_text(
            t["bad_link"]
        )

        return

    if query.data == "video":

        await query.edit_message_text(
            t["processing_video"]
        )

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

                    info = ydl.extract_info(
                        url,
                        download=True
                    )

                    filename = ydl.prepare_filename(info)

                if not os.path.exists(filename):

                    files = os.listdir(temp_dir)

                    if not files:
                        raise FileNotFoundError()

                    filename = os.path.join(
                        temp_dir,
                        files[0]
                    )

                await query.edit_message_text(
                    t["video_ready"]
                )

                with open(filename, "rb") as video:

                    await query.message.reply_video(
                        video=video,
                        caption="🎬 TOJSAVER"
                    )

        except Exception as e:

            print(f"VIDEO ERROR: {e}")

            await query.edit_message_text(
                t["error"]
            )

    elif query.data == "audio":

        await query.edit_message_text(
            t["processing_audio"]
        )

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

                    info = ydl.extract_info(
                        url,
                        download=True
                    )

                    filename = ydl.prepare_filename(info)

                    filename = (
                        os.path.splitext(filename)[0]
                        + ".mp3"
                    )

                if not os.path.exists(filename):

                    raise FileNotFoundError()

                await query.edit_message_text(
                    t["audio_ready"]
                )

                with open(filename, "rb") as audio:

                    await query.message.reply_audio(
                        audio=audio,
                        caption="🎵 TOJSAVER"
                    )

        except Exception as e:

            print(f"AUDIO ERROR: {e}")

            await query.edit_message_text(
                t["error"]
            )


async def callback_handler(update, context):

    query = update.callback_query

    if query.data == "language":

        await language_menu(
            update,
            context
        )

    elif query.data.startswith("lang_"):

        await change_language(
            update,
            context
        )

    elif query.data in ["video", "audio"]:

        await download_media(
            update,
            context
        )

    elif query.data == "menu_video":

        await query.answer()

        lang = get_lang(context)
        t = TEXTS[lang]

        await query.edit_message_text(
            t["choose_format"],
            parse_mode="HTML"
        )

    elif query.data == "menu_audio":

        await query.answer()

        lang = get_lang(context)
        t = TEXTS[lang]

        await query.edit_message_text(
            t["choose_format"],
            parse_mode="HTML"
        )


def main():

    if not TOKEN:

        raise RuntimeError(
            "BOT_TOKEN не найден"
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    print("TOJSAVER 2.0 запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
