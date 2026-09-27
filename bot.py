import os
import re
import sqlite3
import asyncio
import tempfile
import shutil
import time
from datetime import datetime

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
# TOJSAVER V2
# =========================================================
# 🎬 Video Downloader
# 🎵 MP3 Downloader
# 👑 Admin Panel
# 📊 Statistics
# 📢 Broadcast
# 🗄️ SQLite runtime database
#
# Author: JABORZODA FAYZALI
# =========================================================


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

# Твой Telegram ID.
# Здесь оставляем уже установленный ID.
ADMIN_ID = 8479464985

DB_FILE = "tojsaver.db"

MAX_FILE_SIZE = 49 * 1024 * 1024

SUPPORTED_SITES = (
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "tiktok.com",
)


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

        "video":
            "🎬 Скачать видео",

        "audio":
            "🎵 Скачать MP3",

        "stats":
            "📊 Моя статистика",

        "language":
            "🌐 Язык",

        "admin":
            "👑 Админ-панель",

        "back":
            "⬅️ Назад",

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
            "✅ Видео готово!\n\n"
            "🎬 TOJSAVER",

        "audio_ready":
            "✅ MP3 готов!\n\n"
            "🎵 TOJSAVER",

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
            "⚠️ <b>Файл слишком большой для отправки.</b>\n\n"
            "Попробуй другой файл.",

        "language_title":
            "🌐 <b>Выбери язык:</b>",

        "language_changed":
            "✅ Язык изменён.",

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
            "Всего пользователей: <b>{users}</b>\n"
            "Активных за 24 часа: <b>{active}</b>",

        "admin_downloads":
            "📥 <b>СКАЧИВАНИЯ</b>\n\n"
            "Всего: <b>{downloads}</b>\n"
            "🎬 Видео: <b>{videos}</b>\n"
            "🎵 MP3: <b>{audios}</b>",

        "broadcast_start":
            "📢 <b>Рассылка</b>\n\n"
            "Отправь сообщение, которое нужно разослать всем пользователям.\n\n"
            "Для отмены нажми кнопку ниже.",

        "broadcast_cancel":
            "❌ Рассылка отменена.",

        "broadcast_done":
            "📢 <b>Рассылка завершена</b>\n\n"
            "✅ Отправлено: {sent}\n"
            "❌ Ошибок: {failed}",

        "admin_only":
            "⛔ Доступ только для администратора.",

        "users_empty":
            "👥 Пользователей пока нет.",

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

        "video":
            "🎬 Зеркашии видео",

        "audio":
            "🎵 Зеркашии MP3",

        "stats":
            "📊 Статистикаи ман",

        "language":
            "🌐 Забон",

        "admin":
            "👑 Панели админ",

        "back":
            "⬅️ Бозгашт",

        "choose_format":
            "📥 <b>Форматро интихоб кун:</b>",

        "send_link_video":
            "🎬 <b>Зеркашии видео</b>\n\n"
            "🔗 Линкаи Instagram, YouTube ё TikTok-ро фирист.",

        "send_link_audio":
            "🎵 <b>Зеркашии MP3</b>\n\n"
            "🔗 Линкаи Instagram, YouTube ё TikTok-ро фирист.",

        "processing_video":
            "⏳ <b>Видео коркард шуда истодааст...</b>\n\n"
            "🔎 Маълумот гирифта мешавад...\n"
            "📥 Файл зеркашӣ мешавад...\n\n"
            "Лутфан интизор шав.",

        "processing_audio":
            "⏳ <b>Мусиқӣ коркард шуда истодааст...</b>\n\n"
            "🔎 Маълумот гирифта мешавад...\n"
            "🎵 MP3 сохта мешавад...\n\n"
            "Лутфан интизор шав.",

        "video_ready":
            "✅ Видео тайёр!\n\n"
            "🎬 TOJSAVER",

        "audio_ready":
            "✅ MP3 тайёр!\n\n"
            "🎵 TOJSAVER",

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
            "⚠️ <b>Файл хеле калон аст.</b>\n\n"
            "Файли дигарро санҷ.",

        "language_title":
            "🌐 <b>Забонро интихоб кун:</b>",

        "language_changed":
            "✅ Забон иваз шуд.",

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

        "broadcast_start":
            "📢 <b>Рассылка</b>\n\n"
            "Паёмеро фирист, ки ба ҳамаи истифодабарандагон равон шавад.\n\n"
            "Барои бекор кардан тугмаро зер кун.",

        "broadcast_cancel":
            "❌ Рассылка бекор шуд.",

        "broadcast_done":
            "📢 <b>Рассылка анҷом ёфт</b>\n\n"
            "✅ Фиристода шуд: {sent}\n"
            "❌ Хато: {failed}",

        "admin_only":
            "⛔ Танҳо барои администратор.",

        "users_empty":
            "👥 Ҳоло истифодабаранда нест.",

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

        "video":
            "🎬 Download video",

        "audio":
            "🎵 Download MP3",

        "stats":
            "📊 My statistics",

        "language":
            "🌐 Language",

        "admin":
            "👑 Admin panel",

        "back":
            "⬅️ Back",

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
            "🔎 Getting information...\n"
            "📥 Downloading file...\n\n"
            "Please wait.",

        "processing_audio":
            "⏳ <b>Processing music...</b>\n\n"
            "🔎 Getting information...\n"
            "🎵 Creating MP3...\n\n"
            "Please wait.",

        "video_ready":
            "✅ Video ready!\n\n"
            "🎬 TOJSAVER",

        "audio_ready":
            "✅ MP3 ready!\n\n"
            "🎵 TOJSAVER",

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
            "⚠️ <b>File is too large.</b>\n\n"
            "Try another file.",

        "language_title":
            "🌐 <b>Choose language:</b>",

        "language_changed":
            "✅ Language changed.",

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

        "broadcast_start":
            "📢 <b>Broadcast</b>\n\n"
            "Send the message that should be sent to all users.\n\n"
            "Press cancel below to stop.",

        "broadcast_cancel":
            "❌ Broadcast cancelled.",

        "broadcast_done":
            "📢 <b>Broadcast completed</b>\n\n"
            "✅ Sent: {sent}\n"
            "❌ Failed: {failed}",

        "admin_only":
            "⛔ Admin access only.",

        "users_empty":
            "👥 No users yet.",

        "unknown":
            "🤔 I didn't understand.\n\n"
            "Send an Instagram, YouTube or TikTok link.",

    }

}


# =========================================================
# DATABASE
# =========================================================

def db_connection():

    conn = sqlite3.connect(
        DB_FILE,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def init_database():

    conn = db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'ru',
            downloads INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0,
            audios INTEGER DEFAULT 0,
            created_at INTEGER,
            last_seen INTEGER,
            blocked INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            media_type TEXT,
            url TEXT,
            created_at INTEGER,
            success INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_downloads_user
        ON downloads(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_downloads_created
        ON downloads(created_at)
    """)

    conn.commit()
    conn.close()


def db_register_user(user):

    if not user:
        return

    now = int(time.time())

    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (
            user_id,
            username,
            first_name,
            language,
            downloads,
            videos,
            audios,
            created_at,
            last_seen,
            blocked
        )
        VALUES (?, ?, ?, 'ru', 0, 0, 0, ?, ?, 0)

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


def db_set_language(user_id, language):

    conn = db_connection()

    conn.execute("""
        UPDATE users
        SET language = ?
        WHERE user_id = ?
    """, (
        language,
        user_id
    ))

    conn.commit()
    conn.close()


def db_get_language(user_id):

    conn = db_connection()

    row = conn.execute("""
        SELECT language
        FROM users
        WHERE user_id = ?
    """, (
        user_id,
    )).fetchone()

    conn.close()

    if row and row["language"] in TEXTS:
        return row["language"]

    return "ru"


def db_add_download(
    user_id,
    media_type,
    url,
    success=True
):

    now = int(time.time())

    conn = db_connection()

    conn.execute("""
        INSERT INTO downloads (
            user_id,
            media_type,
            url,
            created_at,
            success
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        media_type,
        url,
        now,
        1 if success else 0
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


def db_user_stats(user_id):

    conn = db_connection()

    row = conn.execute("""
        SELECT
            downloads,
            videos,
            audios,
            language
        FROM users
        WHERE user_id = ?
    """, (
        user_id,
    )).fetchone()

    conn.close()

    if not row:
        return {
            "downloads": 0,
            "videos": 0,
            "audios": 0,
            "language": "ru"
        }

    return dict(row)


def db_global_stats():

    conn = db_connection()

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

    day_ago = int(time.time()) - 86400

    active = conn.execute("""
        SELECT COUNT(*) AS c
        FROM users
        WHERE last_seen >= ?
    """, (
        day_ago,
    )).fetchone()["c"]

    conn.close()

    return {
        "users": users,
        "downloads": downloads,
        "videos": videos,
        "audios": audios,
        "active": active
    }


def db_get_users():

    conn = db_connection()

    rows = conn.execute("""
        SELECT
            user_id,
            username,
            first_name,
            downloads,
            videos,
            audios,
            last_seen,
            blocked
        FROM users
        ORDER BY last_seen DESC
    """).fetchall()

    conn.close()

    return rows


def db_mark_blocked(user_id):

    conn = db_connection()

    conn.execute("""
        UPDATE users
        SET blocked = 1
        WHERE user_id = ?
    """, (
        user_id,
    ))

    conn.commit()
    conn.close()


# =========================================================
# HELPERS
# =========================================================

def get_user(update):

    return update.effective_user


def is_admin(update):

    user = get_user(update)

    return bool(
        user and user.id == ADMIN_ID
    )


def get_lang(update, context):

    user = get_user(update)

    if not user:
        return "ru"

    if "lang" in context.user_data:
        return context.user_data["lang"]

    lang = db_get_language(user.id)

    context.user_data["lang"] = lang

    return lang


def register_user(update, context):

    user = get_user(update)

    if not user:
        return

    db_register_user(user)

    if "lang" not in context.user_data:
        context.user_data["lang"] = db_get_language(
            user.id
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


def human_language(lang):

    return {
        "ru": "🇷🇺 Русский",
        "tg": "🇹🇯 Тоҷикӣ",
        "en": "🇬🇧 English"
    }.get(
        lang,
        "🇷🇺 Русский"
    )


# =========================================================
# KEYBOARDS
# =========================================================

def main_keyboard(
    lang,
    admin=False
):

    t = TEXTS[lang]

    rows = [

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
        ]

    ]

    if admin:

        rows.append([
            InlineKeyboardButton(
                t["admin"],
                callback_data="admin_panel"
            )
        ])

    return InlineKeyboardMarkup(rows)


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
                TEXTS[lang]["back"],
                callback_data="back_main"
            )
        ]

    ])


def admin_keyboard(lang):

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
                "📢 Рассылка",
                callback_data="admin_broadcast"
            )
        ],

        [
            InlineKeyboardButton(
                "🔄 Обновить",
                callback_data="admin_refresh"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Главное меню",
                callback_data="back_main"
            )
        ]

    ])


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
        ]

    ])


def cancel_broadcast_keyboard(lang):

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                TEXTS[lang]["back"],
                callback_data="cancel_broadcast"
            )
        ]

    ])


# =========================================================
# DOWNLOAD ENGINE
# =========================================================

def yt_download_sync(
    url,
    media_type,
    temp_dir
):

    output = os.path.join(
        temp_dir,
        "%(title).80s.%(ext)s"
    )

    if media_type == "video":

        options = {

            "outtmpl": output,

            "format":
                "best[ext=mp4]/"
                "best",

            "noplaylist": True,

            "quiet": True,

            "no_warnings": True,

            "restrictfilenames": True,

        }

    else:

        options = {

            "outtmpl": output,

            "format":
                "bestaudio/best",

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
                        "192"
                }

            ]

        }

    with yt_dlp.YoutubeDL(
        options
    ) as ydl:

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
            os.path.join(
                temp_dir,
                f
            )
            for f in os.listdir(
                temp_dir
            )
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

            mp3_files = [
                f for f in files
                if f.lower().endswith(".mp3")
            ]

            if mp3_files:
                filename = mp3_files[0]

        if not os.path.exists(filename):
            filename = files[0]

    return filename


async def download_media(
    update,
    context,
    url,
    media_type
):

    lang = get_lang(
        update,
        context
    )

    chat = update.effective_chat

    if media_type == "video":

        processing_text = TEXTS[lang][
            "processing_video"
        ]

    else:

        processing_text = TEXTS[lang][
            "processing_audio"
        ]

    status = await chat.send_message(
        processing_text,
        parse_mode="HTML"
    )

    temp_dir = tempfile.mkdtemp(
        prefix="tojsaver_"
    )

    try:

        await chat.send_chat_action(
            ChatAction.UPLOAD_VIDEO
            if media_type == "video"
            else ChatAction.UPLOAD_AUDIO
        )

        filename = await asyncio.to_thread(
            yt_download_sync,
            url,
            media_type,
            temp_dir
        )

        if not os.path.exists(filename):

            raise FileNotFoundError()

        file_size = os.path.getsize(
            filename
        )

        if file_size > MAX_FILE_SIZE:

            await status.edit_text(
                TEXTS[lang]["too_large"],
                parse_mode="HTML"
            )

            db_add_download(
                update.effective_user.id,
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
            ) as media:

                await chat.send_video(
                    video=media,
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
            ) as media:

                await chat.send_audio(
                    audio=media,
                    caption="🎵 <b>TOJSAVER</b>",
                    parse_mode="HTML"
                )

        db_add_download(
            update.effective_user.id,
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

        try:

            db_add_download(
                update.effective_user.id,
                media_type,
                url,
                False
            )

        except Exception:
            pass

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )


# =========================================================
# /START
# =========================================================

async def start(
    update,
    context
):

    register_user(
        update,
        context
    )

    lang = get_lang(
        update,
        context
    )

    text = TEXTS[lang]["welcome"]

    keyboard = main_keyboard(
        lang,
        is_admin(update)
    )

    chat_id = update.effective_chat.id

    try:

        if update.message:

            await update.message.delete()

    except Exception:
        pass

    old_message_id = context.user_data.get(
        "menu_message_id"
    )

    if old_message_id:

        try:

            await context.bot.edit_message_text(

                chat_id=chat_id,

                message_id=old_message_id,

                text=text,

                parse_mode="HTML",

                reply_markup=keyboard

            )

            return

        except Exception:
            pass

    message = await context.bot.send_message(

        chat_id=chat_id,

        text=text,

        parse_mode="HTML",

        reply_markup=keyboard

    )

    context.user_data[
        "menu_message_id"
    ] = message.message_id


# =========================================================
# /ADMIN
# =========================================================

async def admin_command(
    update,
    context
):

    register_user(
        update,
        context
    )

    lang = get_lang(
        update,
        context
    )

    if not is_admin(update):

        await update.message.reply_text(
            TEXTS[lang]["admin_only"]
        )

        return

    try:
        await update.message.delete()
    except Exception:
        pass

    await update.effective_chat.send_message(

        TEXTS[lang]["admin_title"],

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# HANDLE TEXT
# =========================================================

async def handle_text(
    update,
    context
):

    register_user(
        update,
        context
    )

    text = (
        update.message.text or ""
    ).strip()

    lang = get_lang(
        update,
        context
    )

    # -----------------------------------------------------
    # ADMIN BROADCAST MODE
    # -----------------------------------------------------

    if (
        is_admin(update)
        and context.user_data.get(
            "broadcast_mode"
        )
    ):

        await perform_broadcast(
            update,
            context,
            update.message
        )

        return

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------

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

        await download_media(
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
# USER STATS
# =========================================================

async def show_user_stats(
    query,
    context
):

    user_id = query.from_user.id

    lang = get_lang(
        None,
        context
    )

    stats = db_user_stats(
        user_id
    )

    await query.edit_message_text(

        TEXTS[lang]["user_stats"].format(

            total=stats["downloads"],

            videos=stats["videos"],

            audios=stats["audios"],

            language=human_language(
                stats["language"]
            )

        ),

        parse_mode="HTML",

        reply_markup=back_keyboard(
            lang
        )

    )


# =========================================================
# ADMIN CHECK
# =========================================================

async def admin_guard(query):

    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "⛔ Access denied.",
            show_alert=True
        )

        return False

    return True


# =========================================================
# ADMIN PANEL
# =========================================================

async def show_admin_panel(
    query,
    context
):

    if not await admin_guard(query):
        return

    lang = get_lang(
        None,
        context
    )

    await query.edit_message_text(

        TEXTS[lang]["admin_title"],

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# ADMIN STATS
# =========================================================

async def show_admin_stats(
    query,
    context
):

    if not await admin_guard(query):
        return

    lang = get_lang(
        None,
        context
    )

    stats = db_global_stats()

    await query.edit_message_text(

        TEXTS[lang]["admin_stats"].format(

            users=stats["users"],

            downloads=stats["downloads"],

            videos=stats["videos"],

            audios=stats["audios"],

            active=stats["active"]

        ),

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# ADMIN USERS
# =========================================================

async def show_admin_users(
    query,
    context
):

    if not await admin_guard(query):
        return

    lang = get_lang(
        None,
        context
    )

    stats = db_global_stats()

    await query.edit_message_text(

        TEXTS[lang]["admin_users"].format(

            users=stats["users"],

            active=stats["active"]

        ),

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# ADMIN DOWNLOADS
# =========================================================

async def show_admin_downloads(
    query,
    context
):

    if not await admin_guard(query):
        return

    lang = get_lang(
        None,
        context
    )

    stats = db_global_stats()

    await query.edit_message_text(

        TEXTS[lang]["admin_downloads"].format(

            downloads=stats["downloads"],

            videos=stats["videos"],

            audios=stats["audios"]

        ),

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# ADMIN USER LIST
# =========================================================

async def show_users_list(
    query,
    context
):

    if not await admin_guard(query):
        return

    lang = get_lang(
        None,
        context
    )

    users = db_get_users()

    if not users:

        await query.edit_message_text(

            TEXTS[lang]["users_empty"],

            reply_markup=admin_keyboard(
                lang
            )

        )

        return

    # Показываем последних пользователей.
    # Это защищает Telegram-сообщение от слишком большого размера.

    users = users[:20]

    lines = [
        "👥 <b>Последние пользователи</b>",
        ""
    ]

    for index, user in enumerate(
        users,
        start=1
    ):

        username = user["username"]

        if username:

            name = (
                "@"
                + username
            )

        else:

            name = (
                user["first_name"]
                or "Без имени"
            )

        lines.append(
            f"{index}. {name} — "
            f"{user['downloads']} 📥"
        )

    await query.edit_message_text(

        "\n".join(lines),

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# BROADCAST
# =========================================================

async def start_broadcast(
    query,
    context
):

    if not await admin_guard(query):
        return

    lang = get_lang(
        None,
        context
    )

    context.user_data[
        "broadcast_mode"
    ] = True

    await query.edit_message_text(

        TEXTS[lang]["broadcast_start"],

        parse_mode="HTML",

        reply_markup=cancel_broadcast_keyboard(
            lang
        )

    )


async def perform_broadcast(
    update,
    context,
    message
):

    if not is_admin(update):

        return

    lang = get_lang(
        update,
        context
    )

    context.user_data.pop(
        "broadcast_mode",
        None
    )

    users = db_get_users()

    sent = 0
    failed = 0

    status = await update.effective_chat.send_message(
        "📢 Рассылка запущена...\n\n"
        "⏳ Подготавливаю пользователей..."
    )

    for user in users:

        user_id = user["user_id"]

        try:

            await context.bot.copy_message(

                chat_id=user_id,

                from_chat_id=message.chat_id,

                message_id=message.message_id

            )

            sent += 1

            await asyncio.sleep(
                0.05
            )

        except Exception as error:

            failed += 1

            print(
                "BROADCAST ERROR:",
                user_id,
                repr(error)
            )

            # Если пользователь заблокировал бота,
            # помечаем его в базе.

            if "blocked" in str(
                error
            ).lower():

                db_mark_blocked(
                    user_id
                )

    await status.edit_text(

        TEXTS[lang]["broadcast_done"].format(

            sent=sent,

            failed=failed

        ),

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def callback_handler(
    update,
    context
):

    query = update.callback_query

    await query.answer()

    data = query.data

    user = query.from_user

    # Создаём/обновляем пользователя,
    # даже если действие пришло через кнопку.

    db_register_user(user)

    if "lang" not in context.user_data:

        context.user_data["lang"] = (
            db_get_language(user.id)
        )

    lang = get_lang(
        None,
        context
    )

    # =====================================================
    # CHOOSE VIDEO
    # =====================================================

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

    # =====================================================
    # CHOOSE AUDIO
    # =====================================================

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

    # =====================================================
    # DOWNLOAD VIDEO
    # =====================================================

    if data == "download_video":

        url = context.user_data.get(
            "url"
        )

        if not url:

            await query.edit_message_text(
                TEXTS[lang]["bad_link"],
                parse_mode="HTML"
            )

            return

        await query.message.delete()

        fake_update = update

        await download_media(
            fake_update,
            context,
            url,
            "video"
        )

        return

    # =====================================================
    # DOWNLOAD AUDIO
    # =====================================================

    if data == "download_audio":

        url = context.user_data.get(
            "url"
        )

        if not url:

            await query.edit_message_text(
                TEXTS[lang]["bad_link"],
                parse_mode="HTML"
            )

            return

        await query.message.delete()

        fake_update = update

        await download_media(
            fake_update,
            context,
            url,
            "audio"
        )

        return

    # =====================================================
    # LANGUAGE
    # =====================================================

    if data == "language":

        await query.edit_message_text(

            TEXTS[lang]["language_title"],

            parse_mode="HTML",

            reply_markup=language_keyboard(
                lang
            )

        )

        return

    # =====================================================
    # CHANGE LANGUAGE
    # =====================================================

    if data.startswith("lang_"):

        new_lang = data.replace(
            "lang_",
            "",
            1
        )

        if new_lang not in TEXTS:

            return

        context.user_data[
            "lang"
        ] = new_lang

        db_set_language(
            user.id,
            new_lang
        )

        await query.edit_message_text(

            TEXTS[new_lang]["menu"],

            parse_mode="HTML",

            reply_markup=main_keyboard(

                new_lang,

                user.id == ADMIN_ID

            )

        )

        return

    # =====================================================
    # USER STATS
    # =====================================================

    if data == "user_stats":

        await show_user_stats(
            query,
            context
        )

        return

    # =====================================================
    # ADMIN PANEL
    # =====================================================

    if data == "admin_panel":

        await show_admin_panel(
            query,
            context
        )

        return

    # =====================================================
    # ADMIN STATS
    # =====================================================

    if data == "admin_stats":

        await show_admin_stats(
            query,
            context
        )

        return

    # =====================================================
    # ADMIN USERS
    # =====================================================

    if data == "admin_users":

        await show_users_list(
            query,
            context
        )

        return

    # =====================================================
    # ADMIN DOWNLOADS
    # =====================================================

    if data == "admin_downloads":

        await show_admin_downloads(
            query,
            context
        )

        return

    # =====================================================
    # ADMIN REFRESH
    # =====================================================

    if data == "admin_refresh":

        await show_admin_stats(
            query,
            context
        )

        return

    # =====================================================
    # ADMIN BROADCAST
    # =====================================================

    if data == "admin_broadcast":

        await start_broadcast(
            query,
            context
        )

        return

    # =====================================================
    # CANCEL BROADCAST
    # =====================================================

    if data == "cancel_broadcast":

        context.user_data.pop(
            "broadcast_mode",
            None
        )

        await query.edit_message_text(

            TEXTS[lang]["broadcast_cancel"],

            reply_markup=admin_keyboard(
                lang
            )

        )

        return

    # =====================================================
    # BACK MAIN
    # =====================================================

    if data == "back_main":

        context.user_data.pop(
            "download_mode",
            None
        )

        context.user_data.pop(
            "broadcast_mode",
            None
        )

        await query.edit_message_text(

            TEXTS[lang]["menu"],

            parse_mode="HTML",

            reply_markup=main_keyboard(

                lang,

                user.id == ADMIN_ID

            )

        )

        context.user_data[
            "menu_message_id"
        ] = query.message.message_id

        return


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update,
    context
):

    print(
        "========================================"
    )

    print(
        "TOJSAVER ERROR:"
    )

    print(
        repr(context.error)
    )

    print(
        "========================================"
    )


# =========================================================
# STARTUP
# =========================================================

async def post_init(
    application
):

    init_database()

    print(
        "========================================"
    )

    print(
        "🎬 TOJSAVER V2"
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
        "========================================"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if not TOKEN:

        raise RuntimeError(
            "BOT_TOKEN не найден в GitHub Secrets"
        )

    init_database()

    app = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    # -----------------------------------------------------
    # COMMANDS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # TEXT
    # -----------------------------------------------------

    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_text
        )
    )

    # -----------------------------------------------------
    # CALLBACKS
    # -----------------------------------------------------

    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    # -----------------------------------------------------
    # ERRORS
    # -----------------------------------------------------

    app.add_error_handler(
        error_handler
    )

    print(
        "🚀 TOJSAVER V2 is running..."
    )

    app.run_polling(
        drop_pending_updates=True
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()
