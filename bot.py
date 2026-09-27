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
ADMIN_ID = 8479464985
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
            "🇹🇯 Video & Music Downloader\n\n"
            "📥 Скачивай доступные видео и музыку "
            "из Instagram, YouTube и TikTok.\n\n"
            "👇 Выбери действие:"
        ),
        "download_video": "📥 Скачать видео",
        "download_audio": "🎵 Скачать MP3",
        "stats": "📊 Моя статистика",
        "language": "🌐 Язык",
        "back": "⬅️ Назад",
        "send_link_video": "🎬 <b>Отправь ссылку на видео:</b>",
        "send_link_audio": "🎵 <b>Отправь ссылку на музыку:</b>",
        "choose_format": "📥 <b>Выбери формат:</b>",
        "video": "🎬 Видео",
        "audio": "🎵 MP3",
        "processing_video": "⏳ Скачиваю видео...",
        "processing_audio": "⏳ Скачиваю музыку...",
        "video_ready": "✅ <b>Видео готово!</b>",
        "audio_ready": "✅ <b>Музыка готова!</b>",
        "error": "❌ Не удалось скачать файл.\n\nПопробуй другую публичную ссылку.",
        "bad_link": "🔗 Отправь корректную ссылку Instagram, YouTube или TikTok.",
        "language_title": "🌐 <b>Выбери язык:</b>",
        "language_changed": "✅ Язык изменён.",
        "stats_text": (
            "📊 <b>Моя статистика</b>\n\n"
            "🎬 Скачано видео: <b>{video}</b>\n"
            "🎵 Скачано MP3: <b>{audio}</b>\n\n"
            "🚀 <b>TOJSAVER</b>"
        ),
    },

    "tg": {
        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇹🇯 Video & Music Downloader\n\n"
            "📥 Видео ва мусиқиро аз Instagram, "
            "YouTube ва TikTok зеркашӣ кун.\n\n"
            "👇 Амалро интихоб кун:"
        ),
        "download_video": "📥 Зеркашии видео",
        "download_audio": "🎵 Зеркашии MP3",
        "stats": "📊 Статистикаи ман",
        "language": "🌐 Забон",
        "back": "⬅️ Бозгашт",
        "send_link_video": "🎬 <b>Линкаи видеоро фирист:</b>",
        "send_link_audio": "🎵 <b>Линкаи мусиқиро фирист:</b>",
        "choose_format": "📥 <b>Форматро интихоб кун:</b>",
        "video": "🎬 Видео",
        "audio": "🎵 MP3",
        "processing_video": "⏳ Видео зеркашӣ шуда истодааст...",
        "processing_audio": "⏳ Мусиқӣ зеркашӣ шуда истодааст...",
        "video_ready": "✅ <b>Видео тайёр!</b>",
        "audio_ready": "✅ <b>Мусиқӣ тайёр!</b>",
        "error": "❌ Файлро зеркашӣ карда натавонистам.\n\nЛинкаи дигарро санҷ.",
        "bad_link": "🔗 Линкаи дурусти Instagram, YouTube ё TikTok-ро фирист.",
        "language_title": "🌐 <b>Забонро интихоб кун:</b>",
        "language_changed": "✅ Забон иваз шуд.",
        "stats_text": (
            "📊 <b>Статистикаи ман</b>\n\n"
            "🎬 Видеоҳои зеркашишуда: <b>{video}</b>\n"
            "🎵 MP3-ҳои зеркашишуда: <b>{audio}</b>\n\n"
            "🚀 <b>TOJSAVER</b>"
        ),
    },

    "en": {
        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇹🇯 Video & Music Downloader\n\n"
            "📥 Download available videos and music "
            "from Instagram, YouTube and TikTok.\n\n"
            "👇 Choose an action:"
        ),
        "download_video": "📥 Download Video",
        "download_audio": "🎵 Download MP3",
        "stats": "📊 My Statistics",
        "language": "🌐 Language",
        "back": "⬅️ Back",
        "send_link_video": "🎬 <b>Send a video link:</b>",
        "send_link_audio": "🎵 <b>Send a music link:</b>",
        "choose_format": "📥 <b>Choose format:</b>",
        "video": "🎬 Video",
        "audio": "🎵 MP3",
        "processing_video": "⏳ Downloading video...",
        "processing_audio": "⏳ Downloading music...",
        "video_ready": "✅ <b>Video ready!</b>",
        "audio_ready": "✅ <b>Music ready!</b>",
        "error": "❌ Failed to download the file.\n\nTry another public link.",
        "bad_link": "🔗 Send a valid Instagram, YouTube or TikTok link.",
        "language_title": "🌐 <b>Choose language:</b>",
        "language_changed": "✅ Language changed.",
        "stats_text": (
            "📊 <b>My Statistics</b>\n\n"
            "🎬 Videos downloaded: <b>{video}</b>\n"
            "🎵 MP3 files downloaded: <b>{audio}</b>\n\n"
            "🚀 <b>TOJSAVER</b>"
        ),
    },
}


def get_lang(context):
    return context.user_data.get("lang", "ru")


def main_keyboard(lang):
    t = TEXTS[lang]

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                t["download_video"],
                callback_data="download_video"
            )
        ],
        [
            InlineKeyboardButton(
                t["download_audio"],
                callback_data="download_audio"
            )
        ],
        [
            InlineKeyboardButton(
                t["stats"],
                callback_data="stats"
            ),
            InlineKeyboardButton(
                t["language"],
                callback_data="language"
            ),
        ],
    ])


def language_keyboard(lang):
    t = TEXTS[lang]

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="lang_tg")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(t["back"], callback_data="back")],
    ])


def back_keyboard(lang):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS[lang]["back"],
                callback_data="back"
            )
        ]
    ])


def format_keyboard(lang):
    t = TEXTS[lang]

    return InlineKeyboardMarkup([
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
                t["back"],
                callback_data="back"
            )
        ],
    ])


async def show_main_menu_message(message, context):
    lang = get_lang(context)

    sent = await message.reply_text(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=main_keyboard(lang),
    )

    context.user_data["menu_message_id"] = sent.message_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)

    # Если это уже сохранённое главное меню,
    # просто обновляем его вместо создания нового.
    menu_id = context.user_data.get("menu_message_id")

    if menu_id:
        try:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=menu_id,
                text=TEXTS[lang]["welcome"],
                parse_mode="HTML",
                reply_markup=main_keyboard(lang),
            )
            return
        except Exception:
            pass

    await show_main_menu_message(
        update.message,
        context
    )


async def show_main_menu(query, context):
    lang = get_lang(context)

    await query.edit_message_text(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=main_keyboard(lang),
    )

    context.user_data["menu_message_id"] = query.message.message_id


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

    mode = context.user_data.get("download_mode")

    if mode == "video":
        context.user_data["download_mode"] = None
        await download_media_direct(
            update,
            context,
            "video"
        )
        return

    if mode == "audio":
        context.user_data["download_mode"] = None
        await download_media_direct(
            update,
            context,
            "audio"
        )
        return

    await update.message.reply_text(
        t["choose_format"],
        parse_mode="HTML",
        reply_markup=format_keyboard(lang),
    )


async def language_menu(update, context):
    query = update.callback_query
    await query.answer()

    lang = get_lang(context)

    await query.edit_message_text(
        TEXTS[lang]["language_title"],
        parse_mode="HTML",
        reply_markup=language_keyboard(lang),
    )


async def change_language(update, context):
    query = update.callback_query
    await query.answer()

    lang = query.data.replace("lang_", "")

    context.user_data["lang"] = lang

    await show_main_menu(query, context)


async def show_stats(update, context):
    query = update.callback_query
    await query.answer()

    lang = get_lang(context)

    video_count = context.user_data.get("video_count", 0)
    audio_count = context.user_data.get("audio_count", 0)

    text = TEXTS[lang]["stats_text"].format(
        video=video_count,
        audio=audio_count,
    )

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard(lang),
    )


async def download_media_direct(update, context, media_type):
    lang = get_lang(context)
    t = TEXTS[lang]

    url = context.user_data.get("url")

    if not url:
        await update.message.reply_text(
            t["bad_link"]
        )
        return

    if media_type == "video":
        status = await update.message.reply_text(
            t["processing_video"]
        )
    else:
        status = await update.message.reply_text(
            t["processing_audio"]
        )

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            output = os.path.join(
                temp_dir,
                "%(title).80s.%(ext)s"
            )

            if media_type == "video":

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

                await status.edit_text(
                    t["video_ready"],
                    parse_mode="HTML"
                )

                with open(filename, "rb") as video:
                    await update.message.reply_video(
                        video=video,
                        caption="🎬 TOJSAVER 🇹🇯"
                    )

                context.user_data["video_count"] = (
                    context.user_data.get(
                        "video_count",
                        0
                    ) + 1
                )

            else:

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

                await status.edit_text(
                    t["audio_ready"],
                    parse_mode="HTML"
                )

                with open(filename, "rb") as audio:
                    await update.message.reply_audio(
                        audio=audio,
                        caption="🎵 TOJSAVER 🇹🇯"
                    )

                context.user_data["audio_count"] = (
                    context.user_data.get(
                        "audio_count",
                        0
                    ) + 1
                )

    except Exception as e:
        print(f"DOWNLOAD ERROR: {e}")

        await status.edit_text(
            t["error"],
            parse_mode="HTML"
        )


async def download_media(update, context):
    query = update.callback_query
    await query.answer()

    lang = get_lang(context)
    t = TEXTS[lang]

    url = context.user_data.get("url")

    if not url:
        await query.edit_message_text(
            t["bad_link"],
            reply_markup=back_keyboard(lang),
        )
        return

    media_type = query.data

    await query.edit_message_text(
        t["processing_video"]
        if media_type == "video"
        else t["processing_audio"]
    )

    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            output = os.path.join(
                temp_dir,
                "%(title).80s.%(ext)s"
            )

            if media_type == "video":

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
                    t["video_ready"],
                    parse_mode="HTML"
                )

                with open(filename, "rb") as video:
                    await query.message.reply_video(
                        video=video,
                        caption="🎬 TOJSAVER 🇹🇯"
                    )

                context.user_data["video_count"] = (
                    context.user_data.get(
                        "video_count",
                        0
                    ) + 1
                )

            else:

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
                    t["audio_ready"],
                    parse_mode="HTML"
                )

                with open(filename, "rb") as audio:
                    await query.message.reply_audio(
                        audio=audio,
                        caption="🎵 TOJSAVER 🇹🇯"
                    )

                context.user_data["audio_count"] = (
                    context.user_data.get(
                        "audio_count",
                        0
                    ) + 1
                )

    except Exception as e:
        print(f"DOWNLOAD ERROR: {e}")

        await query.edit_message_text(
            t["error"],
            parse_mode="HTML"
        )


async def callback_handler(update, context):
    query = update.callback_query
    data = query.data

    if data == "language":
        await language_menu(update, context)

    elif data.startswith("lang_"):
        await change_language(update, context)

    elif data == "stats":
        await show_stats(update, context)

    elif data == "back":
        await query.answer()
        context.user_data["download_mode"] = None
        await show_main_menu(query, context)

    elif data == "download_video":
        await query.answer()

        lang = get_lang(context)

        context.user_data["download_mode"] = "video"

        await query.edit_message_text(
            TEXTS[lang]["send_link_video"],
            parse_mode="HTML",
            reply_markup=back_keyboard(lang),
        )

    elif data == "download_audio":
        await query.answer()

        lang = get_lang(context)

        context.user_data["download_mode"] = "audio"

        await query.edit_message_text(
            TEXTS[lang]["send_link_audio"],
            parse_mode="HTML",
            reply_markup=back_keyboard(lang),
        )

    elif data in ["video", "audio"]:
        context.user_data["download_mode"] = None
        await download_media(update, context)


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не найден")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link
        )
    )

    app.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    print("TOJSAVER PRO запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
