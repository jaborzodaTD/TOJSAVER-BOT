import os
import re
import asyncio
import tempfile
import shutil
import sqlite3
import time

import yt_dlp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================================================
# TOJSAVER
# Clean stable version
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ВСТАВЬ СЮДА СВОЙ СУЩЕСТВУЮЩИЙ ADMIN_ID
ADMIN_ID = 0

DB_FILE = "tojsaver.db"

MAX_FILE_SIZE = 49 * 1024 * 1024

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?"
    r"(?:instagram\.com|youtube\.com|youtu\.be|tiktok\.com)"
    r"/\S+",
    re.IGNORECASE,
)

# =========================================================
# TEXTS
# =========================================================

TEXTS = {
    "ru": {
        "welcome":
            "🎬 <b>TOJSAVER</b>\n\n"
            "🚀 Универсальный загрузчик видео и музыки.\n\n"
            "📥 Instagram\n"
            "📥 YouTube\n"
            "📥 TikTok\n\n"
            "🔗 Просто отправь ссылку.",

        "menu":
            "🎬 <b>TOJSAVER</b>\n\n"
            "Выбери действие:",

        "video": "🎬 Скачать видео",
        "audio": "🎵 Скачать MP3",
        "stats": "📊 Моя статистика",
        "language": "🌐 Язык",
        "admin": "👑 Админ-панель",
        "back": "⬅️ Назад",

        "choose_format":
            "📥 <b>Выбери формат:</b>",

        "send_link_video":
            "🎬 <b>Скачать видео</b>\n\n"
            "🔗 Отправь ссылку на Instagram, YouTube или TikTok.",

        "send_link_audio":
            "🎵 <b>Скачать MP3</b>\n\n"
            "🔗 Отправь ссылку на Instagram, YouTube или TikTok.",

        "processing_video":
            "⏳ <b>Обрабатываю видео...</b>\n\n"
            "🔎 Получаю информацию...\n"
            "📥 Загружаю файл...\n\n"
            "Пожалуйста, подожди.",

        "processing_audio":
            "⏳ <b>Обрабатываю музыку...</b>\n\n"
            "🔎 Получаю информацию...\n"
            "🎵 Создаю MP3...\n\n"
            "Пожалуйста, подожди.",

        "video_ready":
            "✅ Видео готово!\n\n🎬 TOJSAVER",

        "audio_ready":
            "✅ MP3 готов!\n\n🎵 TOJSAVER",

        "bad_link":
            "❌ <b>Ссылка не распознана.</b>\n\n"
            "Поддерживаются:\n"
            "• Instagram\n"
            "• YouTube\n"
            "• TikTok",

        "error":
            "❌ <b>Не удалось скачать файл.</b>\n\n"
            "Попробуй другую ссылку.",

        "too_large":
            "⚠️ <b>Файл слишком большой для отправки.</b>",

        "language_title":
            "🌐 <b>Выбери язык:</b>",

        "user_stats":
            "📊 <b>Твоя статистика</b>\n\n"
            "👤 Скачиваний: {total}\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}\n\n"
            "🌐 Язык: {language}",

        "admin_title":
            "👑 <b>TOJSAVER ADMIN PANEL</b>\n\n"
            "Выбери раздел:",

        "admin_stats":
            "📊 <b>СТАТИСТИКА TOJSAVER</b>\n\n"
            "👥 Пользователей: <b>{users}</b>\n"
            "📥 Скачиваний: <b>{downloads}</b>\n"
            "🎬 Видео: <b>{videos}</b>\n"
            "🎵 MP3: <b>{audios}</b>\n\n"
            "🕒 Активных за 24ч: <b>{active}</b>",

        "admin_users":
            "👥 <b>ПОЛЬЗОВАТЕЛИ</b>\n\n"
            "Всего: <b>{users}</b>\n"
            "Активных за 24 часа: <b>{active}</b>",

        "admin_downloads":
            "📥 <b>СКАЧИВАНИЯ</b>\n\n"
            "Всего: <b>{downloads}</b>\n"
            "🎬 Видео: <b>{videos}</b>\n"
            "🎵 MP3: <b>{audios}</b>",

        "admin_only":
            "⛔ Доступ только для администратора.",

        "unknown":
            "🤔 Я не понял сообщение.\n\n"
            "Отправь ссылку на Instagram, YouTube или TikTok.",
    },

    "tg": {
        "welcome":
            "🎬 <b>TOJSAVER</b>\n\n"
            "🚀 Барномаи зеркашии видео ва мусиқӣ.\n\n"
            "📥 Instagram\n"
            "📥 YouTube\n"
            "📥 TikTok\n\n"
            "🔗 Танҳо линкаро фирист.",

        "menu":
            "🎬 <b>TOJSAVER</b>\n\n"
            "Амалро интихоб кун:",

        "video": "🎬 Зеркашии видео",
        "audio": "🎵 Зеркашии MP3",
        "stats": "📊 Статистикаи ман",
        "language": "🌐 Забон",
        "admin": "👑 Панели админ",
        "back": "⬅️ Бозгашт",

        "choose_format":
            "📥 <b>Форматро интихоб кун:</b>",

        "send_link_video":
            "🎬 <b>Зеркашии видео</b>\n\n"
            "🔗 Линкаи Instagram, YouTube ё TikTok-ро фирист.",

        "send_link_audio":
            "🎵 <b>Зеркашии MP3</b>\n\n"
            "🔗 Линкаи Instagram, YouTube ё TikTok-ро фирист.",

        "processing_video":
            "⏳ <b>Видео коркард мешавад...</b>\n\n"
            "📥 Файл зеркашӣ мешавад...\n\n"
            "Лутфан интизор шав.",

        "processing_audio":
            "⏳ <b>Мусиқӣ коркард мешавад...</b>\n\n"
            "🎵 MP3 сохта мешавад...\n\n"
            "Лутфан интизор шав.",

        "video_ready":
            "✅ Видео тайёр!\n\n🎬 TOJSAVER",

        "audio_ready":
            "✅ MP3 тайёр!\n\n🎵 TOJSAVER",

        "bad_link":
            "❌ <b>Линка шинохта нашуд.</b>\n\n"
            "Дастгирӣ мешавад:\n"
            "• Instagram\n"
            "• YouTube\n"
            "• TikTok",

        "error":
            "❌ <b>Файлро зеркашӣ карда натавонистам.</b>\n\n"
            "Линкаи дигарро санҷ.",

        "too_large":
            "⚠️ <b>Файл хеле калон аст.</b>",

        "language_title":
            "🌐 <b>Забонро интихоб кун:</b>",

        "user_stats":
            "📊 <b>Статистикаи ту</b>\n\n"
            "👤 Ҳамаи зеркашиҳо: {total}\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}\n\n"
            "🌐 Забон: {language}",

        "admin_title":
            "👑 <b>ПАНЕЛИ АДМИНИ TOJSAVER</b>\n\n"
            "Қисмро интихоб кун:",

        "admin_stats":
            "📊 <b>СТАТИСТИКАИ TOJSAVER</b>\n\n"
            "👥 Истифодабарандагон: <b>{users}</b>\n"
            "📥 Зеркашиҳо: <b>{downloads}</b>\n"
            "🎬 Видео: <b>{videos}</b>\n"
            "🎵 MP3: <b>{audios}</b>\n\n"
            "🕒 Фаъол дар 24 соат: <b>{active}</b>",

        "admin_users":
            "👥 <b>ИСТИФОДАБАРАНДАГОН</b>\n\n"
            "Ҳама: <b>{users}</b>\n"
            "Дар 24 соат: <b>{active}</b>",

        "admin_downloads":
            "📥 <b>ЗЕРКАШИҲО</b>\n\n"
            "Ҳама: <b>{downloads}</b>\n"
            "🎬 Видео: <b>{videos}</b>\n"
            "🎵 MP3: <b>{audios}</b>",

        "admin_only":
            "⛔ Танҳо барои администратор.",

        "unknown":
            "🤔 Ман нафаҳмидам.\n\n"
            "Линкаи Instagram, YouTube ё TikTok-ро фирист.",
    },

    "en": {
        "welcome":
            "🎬 <b>TOJSAVER</b>\n\n"
            "🚀 Universal video and music downloader.\n\n"
            "📥 Instagram\n"
            "📥 YouTube\n"
            "📥 TikTok\n\n"
            "🔗 Just send a link.",

        "menu":
            "🎬 <b>TOJSAVER</b>\n\n"
            "Choose an action:",

        "video": "🎬 Download video",
        "audio": "🎵 Download MP3",
        "stats": "📊 My statistics",
        "language": "🌐 Language",
        "admin": "👑 Admin panel",
        "back": "⬅️ Back",

        "choose_format":
            "📥 <b>Choose format:</b>",

        "send_link_video":
            "🎬 <b>Download video</b>\n\n"
            "🔗 Send an Instagram, YouTube or TikTok link.",

        "send_link_audio":
            "🎵 <b>Download MP3</b>\n\n"
            "🔗 Send an Instagram, YouTube or TikTok link.",

        "processing_video":
            "⏳ <b>Processing video...</b>\n\n"
            "📥 Downloading file...\n\n"
            "Please wait.",

        "processing_audio":
            "⏳ <b>Processing music...</b>\n\n"
            "🎵 Creating MP3...\n\n"
            "Please wait.",

        "video_ready":
            "✅ Video ready!\n\n🎬 TOJSAVER",

        "audio_ready":
            "✅ MP3 ready!\n\n🎵 TOJSAVER",

        "bad_link":
            "❌ <b>Link not recognized.</b>\n\n"
            "Supported:\n"
            "• Instagram\n"
            "• YouTube\n"
            "• TikTok",

        "error":
            "❌ <b>Could not download the file.</b>\n\n"
            "Try another link.",

        "too_large":
            "⚠️ <b>File is too large.</b>",

        "language_title":
            "🌐 <b>Choose language:</b>",

        "user_stats":
            "📊 <b>Your statistics</b>\n\n"
            "👤 Downloads: {total}\n"
            "🎬 Videos: {videos}\n"
            "🎵 MP3: {audios}\n\n"
            "🌐 Language: {language}",

        "admin_title":
            "👑 <b>TOJSAVER ADMIN PANEL</b>\n\n"
            "Choose a section:",

        "admin_stats":
            "📊 <b>TOJSAVER STATISTICS</b>\n\n"
            "👥 Users: <b>{users}</b>\n"
            "📥 Downloads: <b>{downloads}</b>\n"
            "🎬 Videos: <b>{videos}</b>\n"
            "🎵 MP3: <b>{audios}</b>\n\n"
            "🕒 Active 24h: <b>{active}</b>",

        "admin_users":
            "👥 <b>USERS</b>\n\n"
            "Total: <b>{users}</b>\n"
            "Active 24h: <b>{active}</b>",

        "admin_downloads":
            "📥 <b>DOWNLOADS</b>\n\n"
            "Total: <b>{downloads}</b>\n"
            "🎬 Videos: <b>{videos}</b>\n"
            "🎵 MP3: <b>{audios}</b>",

        "admin_only":
            "⛔ Admin access only.",

        "unknown":
            "🤔 I didn't understand.\n\n"
            "Send an Instagram, YouTube or TikTok link.",
    }
}

# =========================================================
# DATABASE
# =========================================================

def db():
    conn = sqlite3.connect(
        DB_FILE,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'ru',
            downloads INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0,
            audios INTEGER DEFAULT 0,
            created_at INTEGER,
            last_seen INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            media_type TEXT,
            url TEXT,
            success INTEGER,
            created_at INTEGER
        )
    """)

    conn.commit()
    conn.close()


def register_user(user):
    if not user:
        return

    now = int(time.time())

    conn = db()

    conn.execute("""
        INSERT INTO users (
            user_id,
            username,
            first_name,
            language,
            created_at,
            last_seen
        )
        VALUES (?, ?, ?, 'ru', ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_seen = excluded.last_seen
    """, (
        user.id,
        user.username or "",
        user.first_name or "",
        now,
        now
    ))

    conn.commit()
    conn.close()


def get_language(user_id):
    conn = db()

    row = conn.execute("""
        SELECT language
        FROM users
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    conn.close()

    if row and row["language"] in TEXTS:
        return row["language"]

    return "ru"


def set_language(user_id, language):
    conn = db()

    conn.execute("""
        UPDATE users
        SET language = ?
        WHERE user_id = ?
    """, (language, user_id))

    conn.commit()
    conn.close()


def add_download(
    user_id,
    media_type,
    url,
    success
):
    conn = db()

    conn.execute("""
        INSERT INTO downloads (
            user_id,
            media_type,
            url,
            success,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        media_type,
        url,
        1 if success else 0,
        int(time.time())
    ))

    if success:
        conn.execute("""
            UPDATE users
            SET
                downloads = downloads + 1,
                videos = videos + ?,
                audios = audios + ?
            WHERE user_id = ?
        """, (
            1 if media_type == "video" else 0,
            1 if media_type == "audio" else 0,
            user_id
        ))

    conn.commit()
    conn.close()


# =========================================================
# HELPERS
# =========================================================

def lang_for(update):
    user = update.effective_user

    if not user:
        return "ru"

    return get_language(user.id)


def is_admin(user):
    return bool(
        user and
        ADMIN_ID != 0 and
        user.id == ADMIN_ID
    )


def extract_url(text):
    if not text:
        return None

    match = URL_PATTERN.search(text)

    if not match:
        return None

    return match.group(0).rstrip(
        ".,!?)]}>\"'"
    )


def language_name(lang):
    return {
        "ru": "🇷🇺 Русский",
        "tg": "🇹🇯 Тоҷикӣ",
        "en": "🇬🇧 English",
    }.get(lang, "🇷🇺 Русский")


# =========================================================
# KEYBOARDS
# =========================================================

def main_keyboard(lang, admin=False):

    t = TEXTS[lang]

    buttons = [
        [
            InlineKeyboardButton(
                t["video"],
                callback_data="choose_video"
            )
        ],
        [
            InlineKeyboardButton(
                t["audio"],
                callback_data="choose_audio"
            )
        ],
        [
            InlineKeyboardButton(
                t["stats"],
                callback_data="user_stats"
            )
        ],
        [
            InlineKeyboardButton(
                t["language"],
                callback_data="language"
            )
        ],
    ]

    if admin:
        buttons.append([
            InlineKeyboardButton(
                t["admin"],
                callback_data="admin_panel"
            )
        ])

    return InlineKeyboardMarkup(buttons)


def format_keyboard(lang):

    t = TEXTS[lang]

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                t["video"],
                callback_data="download_video"
            )
        ],
        [
            InlineKeyboardButton(
                t["audio"],
                callback_data="download_audio"
            )
        ],
        [
            InlineKeyboardButton(
                t["back"],
                callback_data="back_main"
            )
        ],
    ])


def back_keyboard(lang):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                TEXTS[lang]["back"],
                callback_data="back_main"
            )
        ]
    ])


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
                callback_data="back_main"
            )
        ]
    ])


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
            )
        ],
        [
            InlineKeyboardButton(
                "📥 Скачивания",
                callback_data="admin_downloads"
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 Обновить",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Главное меню",
                callback_data="back_main"
            )
        ]
    ])


# =========================================================
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    register_user(user)

    lang = get_language(user.id)

    # Чистим старые состояния
    context.user_data.pop(
        "download_mode",
        None
    )

    context.user_data.pop(
        "url",
        None
    )

    try:
        await update.message.delete()
    except Exception:
        pass

    old_id = context.user_data.get(
        "menu_message_id"
    )

    if old_id:

        try:
            message = await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=old_id,
                text=TEXTS[lang]["menu"],
                parse_mode="HTML",
                reply_markup=main_keyboard(
                    lang,
                    is_admin(user)
                )
            )

            context.user_data[
                "menu_message_id"
            ] = message.message_id

            return

        except Exception:
            pass

    message = await update.effective_chat.send_message(
        TEXTS[lang]["menu"],
        parse_mode="HTML",
        reply_markup=main_keyboard(
            lang,
            is_admin(user)
        )
    )

    context.user_data[
        "menu_message_id"
    ] = message.message_id


# =========================================================
# DOWNLOAD
# =========================================================

def download_sync(
    url,
    media_type,
    directory
):

    output = os.path.join(
        directory,
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

        filename = ydl.prepare_filename(
            info
        )

    if media_type == "audio":

        filename = (
            os.path.splitext(filename)[0]
            + ".mp3"
        )

    if not os.path.exists(filename):

        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
        ]

        files = [
            f for f in files
            if os.path.isfile(f)
        ]

        if not files:
            raise FileNotFoundError(
                "Downloaded file not found"
            )

        if media_type == "audio":

            mp3 = [
                f for f in files
                if f.lower().endswith(".mp3")
            ]

            if mp3:
                filename = mp3[0]
            else:
                filename = files[0]

        else:
            filename = files[0]

    return filename


async def send_download(
    update,
    context,
    url,
    media_type
):

    user = update.effective_user
    chat = update.effective_chat

    lang = get_language(
        user.id
    )

    if media_type == "video":
        text = TEXTS[lang]["processing_video"]
    else:
        text = TEXTS[lang]["processing_audio"]

    status = await chat.send_message(
        text,
        parse_mode="HTML"
    )

    directory = tempfile.mkdtemp(
        prefix="tojsaver_"
    )

    try:

        await chat.send_chat_action(
            ChatAction.UPLOAD_VIDEO
            if media_type == "video"
            else ChatAction.UPLOAD_AUDIO
        )

        filename = await asyncio.to_thread(
            download_sync,
            url,
            media_type,
            directory
        )

        if not os.path.exists(filename):
            raise FileNotFoundError()

        size = os.path.getsize(
            filename
        )

        if size > MAX_FILE_SIZE:

            await status.edit_text(
                TEXTS[lang]["too_large"],
                parse_mode="HTML"
            )

            add_download(
                user.id,
                media_type,
                url,
                False
            )

            return

        if media_type == "video":

            await status.edit_text(
                TEXTS[lang]["video_ready"],
                parse_mode="HTML"
            )

            with open(
                filename,
                "rb"
            ) as file:

                await chat.send_video(
                    video=file,
                    caption="🎬 <b>TOJSAVER</b>",
                    parse_mode="HTML"
                )

        else:

            await status.edit_text(
                TEXTS[lang]["audio_ready"],
                parse_mode="HTML"
            )

            with open(
                filename,
                "rb"
            ) as file:

                await chat.send_audio(
                    audio=file,
                    caption="🎵 <b>TOJSAVER</b>",
                    parse_mode="HTML"
                )

        add_download(
            user.id,
            media_type,
            url,
            True
        )

    except Exception as error:

        print(
            "DOWNLOAD ERROR:",
            repr(error)
        )

        try:
            await status.edit_text(
                TEXTS[lang]["error"],
                parse_mode="HTML"
            )
        except Exception:
            pass

        add_download(
            user.id,
            media_type,
            url,
            False
        )

    finally:

        shutil.rmtree(
            directory,
            ignore_errors=True
        )


# =========================================================
# TEXT HANDLER
# =========================================================

async def handle_text(
    update,
    context
):

    user = update.effective_user

    register_user(user)

    lang = get_language(
        user.id
    )

    text = (
        update.message.text or ""
    ).strip()

    url = extract_url(text)

    if not url:

        await update.message.reply_text(
            TEXTS[lang]["unknown"],
            parse_mode="HTML"
        )

        return

    context.user_data[
        "url"
    ] = url

    mode = context.user_data.get(
        "download_mode"
    )

    if mode in (
        "video",
        "audio"
    ):

        context.user_data.pop(
            "download_mode",
            None
        )

        await send_download(
            update,
            context,
            url,
            mode
        )

        return

    await update.message.reply_text(
        TEXTS[lang]["choose_format"],
        parse_mode="HTML",
        reply_markup=format_keyboard(
            lang
        )
    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    user = query.from_user

    print(
        "CALLBACK:",
        user.id,
        query.data
    )

    # КРИТИЧЕСКИ ВАЖНО:
    # подтверждаем callback СРАЗУ.
    try:
        await query.answer()
    except Exception as error:
        print(
            "CALLBACK ANSWER ERROR:",
            repr(error)
        )

    register_user(user)

    # Не используем get_lang(None, context).
    # Берём язык непосредственно по Telegram user ID.
    lang = get_language(
        user.id
    )

    data = query.data

    # -----------------------------------------------------
    # MAIN → VIDEO
    # -----------------------------------------------------

    if data == "choose_video":

        context.user_data[
            "download_mode"
        ] = "video"

        await query.edit_message_text(
            TEXTS[lang]["send_link_video"],
            parse_mode="HTML",
            reply_markup=back_keyboard(
                lang
            )
        )

        return

    # -----------------------------------------------------
    # MAIN → AUDIO
    # -----------------------------------------------------

    if data == "choose_audio":

        context.user_data[
            "download_mode"
        ] = "audio"

        await query.edit_message_text(
            TEXTS[lang]["send_link_audio"],
            parse_mode="HTML",
            reply_markup=back_keyboard(
                lang
            )
        )

        return

    # -----------------------------------------------------
    # VIDEO
    # -----------------------------------------------------

    if data == "download_video":

        url = context.user_data.get(
            "url"
        )

        if not url:

            await query.edit_message_text(
                TEXTS[lang]["bad_link"],
                parse_mode="HTML",
                reply_markup=back_keyboard(
                    lang
                )
            )

            return

        try:
            await query.message.delete()
        except Exception:
            pass

        await send_download(
            update,
            context,
            url,
            "video"
        )

        return

    # -----------------------------------------------------
    # AUDIO
    # -----------------------------------------------------

    if data == "download_audio":

        url = context.user_data.get(
            "url"
        )

        if not url:

            await query.edit_message_text(
                TEXTS[lang]["bad_link"],
                parse_mode="HTML",
                reply_markup=back_keyboard(
                    lang
                )
            )

            return

        try:
            await query.message.delete()
        except Exception:
            pass

        await send_download(
            update,
            context,
            url,
            "audio"
        )

        return

    # -----------------------------------------------------
    # LANGUAGE
    # -----------------------------------------------------

    if data == "language":

        await query.edit_message_text(
            TEXTS[lang]["language_title"],
            parse_mode="HTML",
            reply_markup=language_keyboard(
                lang
            )
        )

        return

    # -----------------------------------------------------
    # CHANGE LANGUAGE
    # -----------------------------------------------------

    if data.startswith("lang_"):

        new_lang = data[
            len("lang_"):
        ]

        if new_lang not in TEXTS:
            return

        set_language(
            user.id,
            new_lang
        )

        context.user_data[
            "lang"
        ] = new_lang

        await query.edit_message_text(
            TEXTS[new_lang]["menu"],
            parse_mode="HTML",
            reply_markup=main_keyboard(
                new_lang,
                is_admin(user)
            )
        )

        return

    # -----------------------------------------------------
    # USER STATS
    # -----------------------------------------------------

    if data == "user_stats":

        conn = db()

        row = conn.execute("""
            SELECT
                downloads,
                videos,
                audios,
                language
            FROM users
            WHERE user_id = ?
        """, (
            user.id,
        )).fetchone()

        conn.close()

        if row:

            total = row["downloads"]
            videos = row["videos"]
            audios = row["audios"]

        else:

            total = 0
            videos = 0
            audios = 0

        await query.edit_message_text(
            TEXTS[lang]["user_stats"].format(
                total=total,
                videos=videos,
                audios=audios,
                language=language_name(lang)
            ),
            parse_mode="HTML",
            reply_markup=back_keyboard(
                lang
            )
        )

        return

    # -----------------------------------------------------
    # ADMIN PANEL
    # -----------------------------------------------------

    if data == "admin_panel":

        if not is_admin(user):

            await query.answer(
                "⛔ Только для администратора.",
                show_alert=True
            )

            return

        await query.edit_message_text(
            TEXTS[lang]["admin_title"],
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )

        return

    # -----------------------------------------------------
    # ADMIN STATS
    # -----------------------------------------------------

    if data == "admin_stats":

        if not is_admin(user):

            await query.answer(
                "⛔ Только для администратора.",
                show_alert=True
            )

            return

        conn = db()

        users = conn.execute("""
            SELECT COUNT(*) AS c
            FROM users
        """).fetchone()["c"]

        downloads = conn.execute("""
            SELECT COUNT(*) AS c
            FROM downloads
            WHERE success = 1
        """).fetchone()["c"]

        videos = conn.execute("""
            SELECT COUNT(*) AS c
            FROM downloads
            WHERE success = 1
            AND media_type = 'video'
        """).fetchone()["c"]

        audios = conn.execute("""
            SELECT COUNT(*) AS c
            FROM downloads
            WHERE success = 1
            AND media_type = 'audio'
        """).fetchone()["c"]

        active = conn.execute("""
            SELECT COUNT(*) AS c
            FROM users
            WHERE last_seen >= ?
        """, (
            int(time.time()) - 86400,
        )).fetchone()["c"]

        conn.close()

        await query.edit_message_text(
            TEXTS[lang]["admin_stats"].format(
                users=users,
                downloads=downloads,
                videos=videos,
                audios=audios,
                active=active
            ),
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )

        return

    # -----------------------------------------------------
    # ADMIN USERS
    # -----------------------------------------------------

    if data == "admin_users":

        if not is_admin(user):

            await query.answer(
                "⛔ Только для администратора.",
                show_alert=True
            )

            return

        conn = db()

        users = conn.execute("""
            SELECT COUNT(*) AS c
            FROM users
        """).fetchone()["c"]

        active = conn.execute("""
            SELECT COUNT(*) AS c
            FROM users
            WHERE last_seen >= ?
        """, (
            int(time.time()) - 86400,
        )).fetchone()["c"]

        conn.close()

        await query.edit_message_text(
            TEXTS[lang]["admin_users"].format(
                users=users,
                active=active
            ),
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )

        return

    # -----------------------------------------------------
    # ADMIN DOWNLOADS
    # -----------------------------------------------------

    if data == "admin_downloads":

        if not is_admin(user):

            await query.answer(
                "⛔ Только для администратора.",
                show_alert=True
            )

            return

        conn = db()

        downloads = conn.execute("""
            SELECT COUNT(*) AS c
            FROM downloads
            WHERE success = 1
        """).fetchone()["c"]

        videos = conn.execute("""
            SELECT COUNT(*) AS c
            FROM downloads
            WHERE success = 1
            AND media_type = 'video'
        """).fetchone()["c"]

        audios = conn.execute("""
            SELECT COUNT(*) AS c
            FROM downloads
            WHERE success = 1
            AND media_type = 'audio'
        """).fetchone()["c"]

        conn.close()

        await query.edit_message_text(
            TEXTS[lang]["admin_downloads"].format(
                downloads=downloads,
                videos=videos,
                audios=audios
            ),
            parse_mode="HTML",
            reply_markup=admin_keyboard()
        )

        return

    # -----------------------------------------------------
    # BACK
    # -----------------------------------------------------

    if data == "back_main":

        context.user_data.pop(
            "download_mode",
            None
        )

        context.user_data.pop(
            "url",
            None
        )

        await query.edit_message_text(
            TEXTS[lang]["menu"],
            parse_mode="HTML",
            reply_markup=main_keyboard(
                lang,
                is_admin(user)
            )
        )

        context.user_data[
            "menu_message_id"
        ] = query.message.message_id

        return

    print(
        "UNKNOWN CALLBACK:",
        data
    )


# =========================================================
# /ADMIN
# =========================================================

async def admin_command(
    update,
    context
):

    user = update.effective_user

    register_user(user)

    lang = get_language(
        user.id
    )

    if not is_admin(user):

        await update.message.reply_text(
            TEXTS[lang]["admin_only"]
        )

        return

    await update.message.reply_text(
        TEXTS[lang]["admin_title"],
        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update,
    context
):

    print(
        "================================"
    )

    print(
        "TOJSAVER ERROR:"
    )

    print(
        repr(context.error)
    )

    print(
        "UPDATE:",
        update
    )

    print(
        "================================"
    )


# =========================================================
# STARTUP
# =========================================================

async def post_init(
    application
):

    init_db()

    print(
        "================================"
    )

    print(
        "🎬 TOJSAVER"
    )

    print(
        "🚀 Bot starting..."
    )

    print(
        "🗄️ Database initialized"
    )

    print(
        "👑 Admin:",
        ADMIN_ID
    )

    print(
        "================================"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN не найден в GitHub Secrets"
        )

    if ADMIN_ID == 0:

        print(
            "⚠️ ADMIN_ID = 0. "
            "Админ-панель будет отключена."
        )

    init_db()

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # /admin
    app.add_handler(
        CommandHandler(
            "admin",
            admin_command
        )
    )

    # КНОПКИ
    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    # ТЕКСТ / ССЫЛКИ
    app.add_handler(
        MessageHandler(
            filters.TEXT &
            ~filters.COMMAND,
            handle_text
        )
    )

    app.add_error_handler(
        error_handler
    )

    print(
        "🚀 TOJSAVER IS RUNNING"
    )

    app.run_polling(
        drop_pending_updates=True
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
