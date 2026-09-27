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

# =========================================================
# 🔐 ADMIN
# =========================================================
# ВСТАВЬ СЮДА СВОЙ TELEGRAM USER ID
ADMIN_ID = 8479464985


# =========================================================
# 🔗 SUPPORTED LINKS
# =========================================================
URL_PATTERN = re.compile(
    r"https?://(?:www\.)?"
    r"(?:instagram\.com|youtube\.com|youtu\.be|tiktok\.com)"
    r"/\S+",
    re.IGNORECASE,
)


# =========================================================
# 🌍 LANGUAGES
# =========================================================
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

        "send_link_video": (
            "🎬 <b>Отправь ссылку на видео:</b>"
        ),
        "send_link_audio": (
            "🎵 <b>Отправь ссылку на музыку:</b>"
        ),

        "choose_format": "📥 <b>Выбери формат:</b>",

        "video": "🎬 Видео",
        "audio": "🎵 MP3",

        "processing_video": (
            "⏳ Скачиваю видео..."
        ),
        "processing_audio": (
            "⏳ Скачиваю музыку..."
        ),

        "video_ready": (
            "✅ <b>Видео готово!</b>"
        ),
        "audio_ready": (
            "✅ <b>Музыка готова!</b>"
        ),

        "error": (
            "❌ Не удалось скачать файл.\n\n"
            "Попробуй другую публичную ссылку."
        ),

        "bad_link": (
            "🔗 Отправь корректную ссылку "
            "Instagram, YouTube или TikTok."
        ),

        "language_title": (
            "🌐 <b>Выбери язык:</b>"
        ),

        "language_changed": (
            "✅ Язык изменён."
        ),

        "stats_text": (
            "📊 <b>Моя статистика</b>\n\n"
            "🎬 Скачано видео: <b>{video}</b>\n"
            "🎵 Скачано MP3: <b>{audio}</b>\n"
            "📥 Всего: <b>{total}</b>"
        ),

        "admin_denied": (
            "⛔ Доступ запрещён."
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

        "send_link_video": (
            "🎬 <b>Линкаи видеоро фирист:</b>"
        ),
        "send_link_audio": (
            "🎵 <b>Линкаи мусиқиро фирист:</b>"
        ),

        "choose_format": (
            "📥 <b>Форматро интихоб кун:</b>"
        ),

        "video": "🎬 Видео",
        "audio": "🎵 MP3",

        "processing_video": (
            "⏳ Видео зеркашӣ шуда истодааст..."
        ),
        "processing_audio": (
            "⏳ Мусиқӣ зеркашӣ шуда истодааст..."
        ),

        "video_ready": (
            "✅ <b>Видео тайёр!</b>"
        ),
        "audio_ready": (
            "✅ <b>Мусиқӣ тайёр!</b>"
        ),

        "error": (
            "❌ Файлро зеркашӣ карда натавонистам.\n\n"
            "Линкаи дигарро санҷ."
        ),

        "bad_link": (
            "🔗 Линкаи дурусти Instagram, "
            "YouTube ё TikTok-ро фирист."
        ),

        "language_title": (
            "🌐 <b>Забонро интихоб кун:</b>"
        ),

        "language_changed": (
            "✅ Забон иваз шуд."
        ),

        "stats_text": (
            "📊 <b>Статистикаи ман</b>\n\n"
            "🎬 Видеоҳои зеркашишуда: <b>{video}</b>\n"
            "🎵 MP3-ҳои зеркашишуда: <b>{audio}</b>\n"
            "📥 Ҳамагӣ: <b>{total}</b>"
        ),

        "admin_denied": (
            "⛔ Дастрасӣ манъ аст."
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

        "send_link_video": (
            "🎬 <b>Send a video link:</b>"
        ),
        "send_link_audio": (
            "🎵 <b>Send a music link:</b>"
        ),

        "choose_format": (
            "📥 <b>Choose format:</b>"
        ),

        "video": "🎬 Video",
        "audio": "🎵 MP3",

        "processing_video": (
            "⏳ Downloading video..."
        ),
        "processing_audio": (
            "⏳ Downloading music..."
        ),

        "video_ready": (
            "✅ <b>Video ready!</b>"
        ),
        "audio_ready": (
            "✅ <b>Music ready!</b>"
        ),

        "error": (
            "❌ Failed to download the file.\n\n"
            "Try another public link."
        ),

        "bad_link": (
            "🔗 Send a valid Instagram, "
            "YouTube or TikTok link."
        ),

        "language_title": (
            "🌐 <b>Choose language:</b>"
        ),

        "language_changed": (
            "✅ Language changed."
        ),

        "stats_text": (
            "📊 <b>My Statistics</b>\n\n"
            "🎬 Videos downloaded: <b>{video}</b>\n"
            "🎵 MP3 files downloaded: <b>{audio}</b>\n"
            "📥 Total: <b>{total}</b>"
        ),

        "admin_denied": (
            "⛔ Access denied."
        ),
    },
}


# =========================================================
# 🧠 HELPERS
# =========================================================
def get_lang(context):
    return context.user_data.get("lang", "ru")


def is_admin(update):
    user = update.effective_user

    if not user:
        return False

    return user.id == ADMIN_ID


def register_user(update, context):
    user = update.effective_user

    if not user:
        return

    users = context.application.bot_data.setdefault(
        "users",
        set()
    )

    users.add(user.id)


# =========================================================
# 🏠 MAIN MENU
# =========================================================
def main_keyboard(lang, show_admin=False):
    t = TEXTS[lang]

    keyboard = [
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
    ]

    if show_admin:
        keyboard.append([
            InlineKeyboardButton(
                "👑 Админ-панель",
                callback_data="admin_panel"
            )
        ])

    return InlineKeyboardMarkup(keyboard)


def language_keyboard(lang):
    t = TEXTS[lang]

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🇹🇯 Тоҷикӣ",
                callback_data="lang_tg"
            )
        ],
        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="lang_ru"
            )
        ],
        [
            InlineKeyboardButton(
                "🇬🇧 English",
                callback_data="lang_en"
            )
        ],
        [
            InlineKeyboardButton(
                t["back"],
                callback_data="back"
            )
        ],
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


# =========================================================
# 👑 ADMIN MENU
# =========================================================
def admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 Статистика",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Пользователи",
                callback_data="admin_users"
            ),
            InlineKeyboardButton(
                "📥 Скачивания",
                callback_data="admin_downloads"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Главное меню",
                callback_data="back"
            )
        ],
    ])


# =========================================================
# 🚀 START
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update, context)

    lang = get_lang(context)

    show_admin = is_admin(update)

    menu_id = context.user_data.get(
        "menu_message_id"
    )

    if menu_id:

        try:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=menu_id,
                text=TEXTS[lang]["welcome"],
                parse_mode="HTML",
                reply_markup=main_keyboard(
                    lang,
                    show_admin
                ),
            )

            return

        except Exception:
            pass

    sent = await update.message.reply_text(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=main_keyboard(
            lang,
            show_admin
        ),
    )

    context.user_data["menu_message_id"] = (
        sent.message_id
    )


# =========================================================
# 🔗 LINK HANDLER
# =========================================================
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    register_user(update, context)

    lang = get_lang(context)
    t = TEXTS[lang]

    text = update.message.text.strip()

    match = URL_PATTERN.search(text)

    if not match:

        await update.message.reply_text(
            t["bad_link"]
        )

        return

    url = match.group(0)

    context.user_data["url"] = url

    mode = context.user_data.get(
        "download_mode"
    )

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


# =========================================================
# 🌍 LANGUAGE
# =========================================================
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

    lang = query.data.replace(
        "lang_",
        ""
    )

    context.user_data["lang"] = lang

    await show_main_menu(
        query,
        context
    )


# =========================================================
# 📊 USER STATISTICS
# =========================================================
async def show_stats(update, context):

    query = update.callback_query

    await query.answer()

    lang = get_lang(context)

    video_count = context.user_data.get(
        "video_count",
        0
    )

    audio_count = context.user_data.get(
        "audio_count",
        0
    )

    total = video_count + audio_count

    text = TEXTS[lang]["stats_text"].format(
        video=video_count,
        audio=audio_count,
        total=total,
    )

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard(lang),
    )


# =========================================================
# 👑 ADMIN COMMAND
# =========================================================
async def admin_command(update, context):

    register_user(update, context)

    if not is_admin(update):

        lang = get_lang(context)

        await update.message.reply_text(
            TEXTS[lang]["admin_denied"]
        )

        return

    await update.message.reply_text(
        "👑 <b>TOJSAVER ADMIN PANEL</b>\n\n"
        "🔐 Доступ разрешён.\n\n"
        "Выбери раздел:",
        parse_mode="HTML",
        reply_markup=admin_keyboard(),
    )


# =========================================================
# 👑 ADMIN PANEL
# =========================================================
async def admin_panel(update, context):

    query = update.callback_query

    if not is_admin(update):

        await query.answer(
            "⛔ Доступ запрещён.",
            show_alert=True
        )

        return

    await query.answer()

    await query.edit_message_text(
        "👑 <b>TOJSAVER ADMIN PANEL</b>\n\n"
        "🔐 Доступ разрешён.\n\n"
        "Выбери раздел:",
        parse_mode="HTML",
        reply_markup=admin_keyboard(),
    )


# =========================================================
# 📊 ADMIN STATISTICS
# =========================================================
async def admin_stats(update, context):

    query = update.callback_query

    if not is_admin(update):

        await query.answer(
            "⛔ Доступ запрещён.",
            show_alert=True
        )

        return

    await query.answer()

    users = context.application.bot_data.get(
        "users",
        set()
    )

    video = context.application.bot_data.get(
        "video_count",
        0
    )

    audio = context.application.bot_data.get(
        "audio_count",
        0
    )

    total = video + audio

    await query.edit_message_text(
        "📊 <b>TOJSAVER — Статистика</b>\n\n"
        f"👥 Пользователей: <b>{len(users)}</b>\n"
        f"🎬 Видео: <b>{video}</b>\n"
        f"🎵 MP3: <b>{audio}</b>\n"
        f"📥 Всего скачиваний: <b>{total}</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard(),
    )


# =========================================================
# 👥 ADMIN USERS
# =========================================================
async def admin_users(update, context):

    query = update.callback_query

    if not is_admin(update):

        await query.answer(
            "⛔ Доступ запрещён.",
            show_alert=True
        )

        return

    await query.answer()

    users = context.application.bot_data.get(
        "users",
        set()
    )

    await query.edit_message_text(
        "👥 <b>Пользователи</b>\n\n"
        f"Всего пользователей: <b>{len(users)}</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard(),
    )


# =========================================================
# 📥 ADMIN DOWNLOADS
# =========================================================
async def admin_downloads(update, context):

    query = update.callback_query

    if not is_admin(update):

        await query.answer(
            "⛔ Доступ запрещён.",
            show_alert=True
        )

        return

    await query.answer()

    video = context.application.bot_data.get(
        "video_count",
        0
    )

    audio = context.application.bot_data.get(
        "audio_count",
        0
    )

    total = video + audio

    await query.edit_message_text(
        "📥 <b>Скачивания</b>\n\n"
        f"🎬 Видео: <b>{video}</b>\n"
        f"🎵 MP3: <b>{audio}</b>\n"
        f"📦 Всего: <b>{total}</b>",
        parse_mode="HTML",
        reply_markup=admin_keyboard(),
    )


# =========================================================
# 🎬 DIRECT DOWNLOAD
# =========================================================
async def download_media_direct(
    update,
    context,
    media_type
):

    lang = get_lang(context)
    t = TEXTS[lang]

    url = context.user_data.get(
        "url"
    )

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

                with yt_dlp.YoutubeDL(
                    options
                ) as ydl:

                    info = ydl.extract_info(
                        url,
                        download=True
                    )

                    filename = (
                        ydl.prepare_filename(
                            info
                        )
                    )

                if not os.path.exists(
                    filename
                ):

                    files = os.listdir(
                        temp_dir
                    )

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

                with open(
                    filename,
                    "rb"
                ) as video:

                    await update.message.reply_video(
                        video=video,
                        caption="🎬 TOJSAVER 🇹🇯"
                    )

                context.user_data[
                    "video_count"
                ] = (
                    context.user_data.get(
                        "video_count",
                        0
                    ) + 1
                )

                context.application.bot_data[
                    "video_count"
                ] = (
                    context.application.bot_data.get(
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
                            "key":
                                "FFmpegExtractAudio",
                            "preferredcodec":
                                "mp3",
                            "preferredquality":
                                "192",
                        }
                    ],
                }

                with yt_dlp.YoutubeDL(
                    options
                ) as ydl:

                    info = ydl.extract_info(
                        url,
                        download=True
                    )

                    filename = (
                        ydl.prepare_filename(
                            info
                        )
                    )

                    filename = (
                        os.path.splitext(
                            filename
                        )[0]
                        + ".mp3"
                    )

                if not os.path.exists(
                    filename
                ):

                    raise FileNotFoundError()

                await status.edit_text(
                    t["audio_ready"],
                    parse_mode="HTML"
                )

                with open(
                    filename,
                    "rb"
                ) as audio:

                    await update.message.reply_audio(
                        audio=audio,
                        caption="🎵 TOJSAVER 🇹🇯"
                    )

                context.user_data[
                    "audio_count"
                ] = (
                    context.user_data.get(
                        "audio_count",
                        0
                    ) + 1
                )

                context.application.bot_data[
                    "audio_count"
                ] = (
                    context.application.bot_data.get(
                        "audio_count",
                        0
                    ) + 1
                )

    except Exception as e:

        print(
            f"DOWNLOAD ERROR: {e}"
        )

        await status.edit_text(
            t["error"],
            parse_mode="HTML"
        )


# =========================================================
# 🎬 CALLBACK DOWNLOAD
# =========================================================
async def download_media(
    update,
    context
):

    query = update.callback_query

    await query.answer()

    lang = get_lang(context)
    t = TEXTS[lang]

    url = context.user_data.get(
        "url"
    )

    if not url:

        await query.edit_message_text(
            t["bad_link"],
            reply_markup=back_keyboard(
                lang
            ),
        )

        return

    media_type = query.data

    if media_type == "video":

        await query.edit_message_text(
            t["processing_video"]
        )

    else:

        await query.edit_message_text(
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

                with yt_dlp.YoutubeDL(
                    options
                ) as ydl:

                    info = ydl.extract_info(
                        url,
                        download=True
                    )

                    filename = (
                        ydl.prepare_filename(
                            info
                        )
                    )

                if not os.path.exists(
                    filename
                ):

                    files = os.listdir(
                        temp_dir
                    )

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

                with open(
                    filename,
                    "rb"
                ) as video:

                    await query.message.reply_video(
                        video=video,
                        caption="🎬 TOJSAVER 🇹🇯"
                    )

                context.user_data[
                    "video_count"
                ] = (
                    context.user_data.get(
                        "video_count",
                        0
                    ) + 1
                )

                context.application.bot_data[
                    "video_count"
                ] = (
                    context.application.bot_data.get(
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
                            "key":
                                "FFmpegExtractAudio",
                            "preferredcodec":
                                "mp3",
                            "preferredquality":
                                "192",
                        }
                    ],
                }

                with yt_dlp.YoutubeDL(
                    options
                ) as ydl:

                    info = ydl.extract_info(
                        url,
                        download=True
                    )

                    filename = (
                        ydl.prepare_filename(
                            info
                        )
                    )

                    filename = (
                        os.path.splitext(
                            filename
                        )[0]
                        + ".mp3"
                    )

                if not os.path.exists(
                    filename
                ):

                    raise FileNotFoundError()

                await query.edit_message_text(
                    t["audio_ready"],
                    parse_mode="HTML"
                )

                with open(
                    filename,
                    "rb"
                ) as audio:

                    await query.message.reply_audio(
                        audio=audio,
                        caption="🎵 TOJSAVER 🇹🇯"
                    )

                context.user_data[
                    "audio_count"
                ] = (
                    context.user_data.get(
                        "audio_count",
                        0
                    ) + 1
                )

                context.application.bot_data[
                    "audio_count"
                ] = (
                    context.application.bot_data.get(
                        "audio_count",
                        0
                    ) + 1
                )

    except Exception as e:

        print(
            f"DOWNLOAD ERROR: {e}"
        )

        await query.edit_message_text(
            t["error"],
            parse_mode="HTML"
        )


# =========================================================
# 🎛 CALLBACK HANDLER
# =========================================================
async def callback_handler(
    update,
    context
):

    query = update.callback_query

    data = query.data

    # -------------------------
    # LANGUAGE
    # -------------------------
    if data == "language":

        await language_menu(
            update,
            context
        )

    elif data.startswith(
        "lang_"
    ):

        await change_language(
            update,
            context
        )

    # -------------------------
    # USER STATS
    # -------------------------
    elif data == "stats":

        await show_stats(
            update,
            context
        )

    # -------------------------
    # BACK
    # -------------------------
    elif data == "back":

        await query.answer()

        context.user_data[
            "download_mode"
        ] = None

        await show_main_menu(
            query,
            context
        )

    # -------------------------
    # DOWNLOAD VIDEO
    # -------------------------
    elif data == "download_video":

        await query.answer()

        lang = get_lang(
            context
        )

        context.user_data[
            "download_mode"
        ] = "video"

        await query.edit_message_text(
            TEXTS[lang][
                "send_link_video"
            ],
            parse_mode="HTML",
            reply_markup=back_keyboard(
                lang
            ),
        )

    # -------------------------
    # DOWNLOAD MP3
    # -------------------------
    elif data == "download_audio":

        await query.answer()

        lang = get_lang(
            context
        )

        context.user_data[
            "download_mode"
        ] = "audio"

        await query.edit_message_text(
            TEXTS[lang][
                "send_link_audio"
            ],
            parse_mode="HTML",
            reply_markup=back_keyboard(
                lang
            ),
        )

    # -------------------------
    # FORMAT
    # -------------------------
    elif data in [
        "video",
        "audio"
    ]:

        context.user_data[
            "download_mode"
        ] = None

        await download_media(
            update,
            context
        )

    # -------------------------
    # ADMIN PANEL
    # -------------------------
    elif data == "admin_panel":

        await admin_panel(
            update,
            context
        )

    elif data == "admin_stats":

        await admin_stats(
            update,
            context
        )

    elif data == "admin_users":

        await admin_users(
            update,
            context
        )

    elif data == "admin_downloads":

        await admin_downloads(
            update,
            context
        )


# =========================================================
# 🏁 MAIN
# =========================================================
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
        CommandHandler(
            "admin",
            admin_command
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_link
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    print(
        "TOJSAVER PRO + ADMIN запущен!"
    )

    app.run_polling()


if __name__ == "__main__":
    main()
