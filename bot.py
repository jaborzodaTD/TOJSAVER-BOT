import asyncio
import logging
import os
import re
import sqlite3
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

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

# ============================================================
# TOJSAVER — V3
# Modern Telegram Video & Music Downloader
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Optional administrator ID.
# If ADMIN_ID is not configured, admin statistics are disabled.
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except ValueError:
    ADMIN_ID = 8479464985

APP_NAME = "TOJSAVER"
BOT_USERNAME = "@TojSaverBot"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOWNLOAD_DIR = BASE_DIR / "downloads"
DB_FILE = DATA_DIR / "tojsaver.db"

DATA_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Maximum local file size we are willing to send.
# Keep this conservative for Telegram bots.
MAX_FILE_SIZE_MB = 49
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

DOWNLOAD_TIMEOUT = 240
MAX_CONCURRENT_DOWNLOADS = 3

download_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(APP_NAME)

# ============================================================
# DATABASE
# ============================================================


def db_connection():
    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'tg',
            downloads INTEGER DEFAULT 0,
            joined_at INTEGER,
            last_seen INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            media_type TEXT,
            url TEXT,
            success INTEGER DEFAULT 0,
            error TEXT,
            created_at INTEGER
        )
        """
    )

    conn.commit()
    conn.close()


def register_user(user):
    if not user:
        return

    now = int(time.time())

    conn = db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (
            user_id,
            username,
            first_name,
            language,
            downloads,
            joined_at,
            last_seen
        )
        VALUES (?, ?, ?, 'tg', 0, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_seen = excluded.last_seen
        """,
        (
            user.id,
            user.username or "",
            user.first_name or "",
            now,
            now,
        ),
    )

    conn.commit()
    conn.close()


def get_language(user_id):
    conn = db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT language FROM users WHERE user_id = ?",
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()

    if row and row["language"]:
        return row["language"]

    return "tg"


def set_language(user_id, language):
    conn = db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (
            user_id,
            language,
            joined_at,
            last_seen
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET language = excluded.language
        """,
        (
            user_id,
            language,
            int(time.time()),
            int(time.time()),
        ),
    )

    conn.commit()
    conn.close()


def record_download(
    user_id,
    platform,
    media_type,
    url,
    success,
    error="",
):
    conn = db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO downloads (
            user_id,
            platform,
            media_type,
            url,
            success,
            error,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            platform,
            media_type,
            url,
            1 if success else 0,
            error[:1000],
            int(time.time()),
        ),
    )

    if success:
        cur.execute(
            """
            UPDATE users
            SET downloads = downloads + 1
            WHERE user_id = ?
            """,
            (user_id,),
        )

    conn.commit()
    conn.close()


def get_statistics():
    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM users")
    users = cur.fetchone()["total"]

    cur.execute(
        "SELECT COUNT(*) AS total FROM downloads WHERE success = 1"
    )
    successful = cur.fetchone()["total"]

    cur.execute(
        "SELECT COUNT(*) AS total FROM downloads WHERE success = 0"
    )
    failed = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM downloads")
    total = cur.fetchone()["total"]

    conn.close()

    return {
        "users": users,
        "successful": successful,
        "failed": failed,
        "total": total,
    }


# ============================================================
# TEXTS
# ============================================================

TEXTS = {
    "tg": {
        "welcome": (
            "👋 Салом! Ман <b>TOJSAVER</b> ҳастам.\n\n"
            "🎬 Видео аз Instagram, TikTok ва YouTube\n"
            "🎵 Аудио / MP3\n"
            "⚡️ Танҳо линкро фирист!\n\n"
            "👇 Аз меню интихоб кун:"
        ),
        "help": (
            "📖 <b>Чӣ тавр истифода бурдан?</b>\n\n"
            "1️⃣ Линки видеоиро нусха кун\n"
            "2️⃣ Ба TOJSAVER фирист\n"
            "3️⃣ Видео ё MP3-ро интихоб кун\n"
            "4️⃣ Чанд лаҳза интизор шав\n\n"
            "🔗 Платформаҳо:\n"
            "• Instagram\n"
            "• TikTok\n"
            "• YouTube\n\n"
            "⚠️ Танҳо контенти дастрас ва иҷозатдодашударо истифода бар."
        ),
        "choose": "🎯 Форматро интихоб кун:",
        "downloading": "⏳ Видео тайёр карда шуда истодааст...\n\n📥 Лутфан каме интизор шав.",
        "processing": "⚙️ Файл коркард шуда истодааст...",
        "success": "✅ Тайёр! 🎉",
        "error": (
            "❌ <b>Файлро скачат карда натавонистам.</b>\n\n"
            "🔄 Линки дигарро санҷ.\n\n"
            "Агар проблема давом кунад, эҳтимол платформа "
            "ин контентро барои скачат дастрас намекунад."
        ),
        "invalid": "❌ Ин линк дуруст нест. Линки Instagram, TikTok ё YouTube фирист.",
        "cancelled": "🛑 Амалиёт бекор карда шуд.",
        "language": "🌐 Забонро интихоб кун:",
        "stats_denied": "⛔️ Ин команда танҳо барои администратор аст.",
    },

    "ru": {
        "welcome": (
            "👋 Привет! Я <b>TOJSAVER</b>.\n\n"
            "🎬 Видео из Instagram, TikTok и YouTube\n"
            "🎵 Аудио / MP3\n"
            "⚡️ Просто отправь ссылку!\n\n"
            "👇 Выбери действие:"
        ),
        "help": (
            "📖 <b>Как пользоваться?</b>\n\n"
            "1️⃣ Скопируй ссылку на видео\n"
            "2️⃣ Отправь её TOJSAVER\n"
            "3️⃣ Выбери Видео или MP3\n"
            "4️⃣ Подожди несколько секунд\n\n"
            "🔗 Платформы:\n"
            "• Instagram\n"
            "• TikTok\n"
            "• YouTube\n\n"
            "⚠️ Используй только доступный и разрешённый контент."
        ),
        "choose": "🎯 Выбери формат:",
        "downloading": "⏳ Подготавливаю файл...\n\n📥 Подожди немного.",
        "processing": "⚙️ Обрабатываю файл...",
        "success": "✅ Готово! 🎉",
        "error": (
            "❌ <b>Не удалось скачать файл.</b>\n\n"
            "🔄 Попробуй другую ссылку.\n\n"
            "Если ошибка повторяется, платформа может "
            "не предоставлять этот контент для скачивания."
        ),
        "invalid": "❌ Неверная ссылка. Отправь ссылку Instagram, TikTok или YouTube.",
        "cancelled": "🛑 Операция отменена.",
        "language": "🌐 Выбери язык:",
        "stats_denied": "⛔️ Эта команда доступна только администратору.",
    },

    "en": {
        "welcome": (
            "👋 Hello! I'm <b>TOJSAVER</b>.\n\n"
            "🎬 Video from Instagram, TikTok and YouTube\n"
            "🎵 Audio / MP3\n"
            "⚡️ Just send a link!\n\n"
            "👇 Choose an action:"
        ),
        "help": (
            "📖 <b>How to use?</b>\n\n"
            "1️⃣ Copy a video link\n"
            "2️⃣ Send it to TOJSAVER\n"
            "3️⃣ Choose Video or MP3\n"
            "4️⃣ Wait a few seconds\n\n"
            "🔗 Platforms:\n"
            "• Instagram\n"
            "• TikTok\n"
            "• YouTube\n\n"
            "⚠️ Use only accessible and permitted content."
        ),
        "choose": "🎯 Choose a format:",
        "downloading": "⏳ Preparing your file...\n\n📥 Please wait.",
        "processing": "⚙️ Processing the file...",
        "success": "✅ Done! 🎉",
        "error": (
            "❌ <b>Unable to download the file.</b>\n\n"
            "🔄 Try another link.\n\n"
            "The platform may not make this content "
            "available for downloading."
        ),
        "invalid": "❌ Invalid link. Send an Instagram, TikTok or YouTube link.",
        "cancelled": "🛑 Operation cancelled.",
        "language": "🌐 Choose language:",
        "stats_denied": "⛔️ Admin only.",
    },
}


def t(user_id, key):
    lang = get_language(user_id)

    if lang not in TEXTS:
        lang = "tg"

    return TEXTS[lang].get(key, key)


# ============================================================
# KEYBOARDS
# ============================================================


def main_keyboard(user_id):
    lang = get_language(user_id)

    if lang == "ru":
        rows = [
            [
                InlineKeyboardButton("🎬 Скачать видео", callback_data="video"),
                InlineKeyboardButton("🎵 MP3", callback_data="audio"),
            ],
            [
                InlineKeyboardButton("🌐 Язык", callback_data="language"),
                InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
            ],
        ]

    elif lang == "en":
        rows = [
            [
                InlineKeyboardButton("🎬 Video", callback_data="video"),
                InlineKeyboardButton("🎵 MP3", callback_data="audio"),
            ],
            [
                InlineKeyboardButton("🌐 Language", callback_data="language"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            ],
        ]

    else:
        rows = [
            [
                InlineKeyboardButton("🎬 Видео", callback_data="video"),
                InlineKeyboardButton("🎵 MP3", callback_data="audio"),
            ],
            [
                InlineKeyboardButton("🌐 Забон", callback_data="language"),
                InlineKeyboardButton("ℹ️ Ёрдам", callback_data="help"),
            ],
        ]

    return InlineKeyboardMarkup(rows)


def format_keyboard(user_id, url):
    lang = get_language(user_id)

    # URL itself is NOT placed into callback_data.
    # This avoids Telegram's callback_data 64-byte limitation.
    if lang == "ru":
        text_video = "🎬 Видео"
        text_audio = "🎵 MP3"
        text_cancel = "❌ Отмена"

    elif lang == "en":
        text_video = "🎬 Video"
        text_audio = "🎵 MP3"
        text_cancel = "❌ Cancel"

    else:
        text_video = "🎬 Видео"
        text_audio = "🎵 MP3"
        text_cancel = "❌ Бекор кардан"

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text_video,
                    callback_data="download_video",
                ),
                InlineKeyboardButton(
                    text_audio,
                    callback_data="download_audio",
                ),
            ],
            [
                InlineKeyboardButton(
                    text_cancel,
                    callback_data="cancel",
                )
            ],
        ]
    )


def language_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="lang_tg"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            ],
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
            ],
        ]
    )


# ============================================================
# URL DETECTION
# ============================================================


URL_REGEX = re.compile(
    r"https?://[^\s<>()]+",
    re.IGNORECASE,
)


def extract_url(text):
    if not text:
        return None

    match = URL_REGEX.search(text)

    if not match:
        return None

    url = match.group(0).rstrip(".,!?)]}")

    return url


def detect_platform(url):
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return "unknown"

    host = host.replace("www.", "")

    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"

    if "instagram.com" in host:
        return "instagram"

    if "tiktok.com" in host:
        return "tiktok"

    return "unknown"


def is_supported_url(url):
    return detect_platform(url) in {
        "youtube",
        "instagram",
        "tiktok",
    }


# ============================================================
# TEMP FILE CLEANUP
# ============================================================


def cleanup_files(files):
    for file_path in files:
        try:
            path = Path(file_path)

            if path.exists():
                path.unlink()
        except Exception:
            pass


def cleanup_download_directory():
    now = time.time()

    for path in DOWNLOAD_DIR.iterdir():
        try:
            if not path.is_file():
                continue

            age = now - path.stat().st_mtime

            if age > 3600:
                path.unlink()
        except Exception:
            pass


# ============================================================
# YT-DLP
# ============================================================


def build_yt_dlp_command(url, mode, output_template):
    common = [
        "yt-dlp",
        "--no-playlist",
        "--no-warnings",
        "--ignore-errors",
        "--retries",
        "5",
        "--fragment-retries",
        "5",
        "--retry-sleep",
        "1",
        "--socket-timeout",
        "30",
        "--connect-timeout",
        "30",
        "--extractor-retries",
        "3",
        "--concurrent-fragments",
        "3",
        "--restrict-filenames",
        "--no-part",
        "--newline",
        "-o",
        output_template,
    ]

    # Browser-like headers.
    common += [
        "--add-header",
        "User-Agent: Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36",
    ]

    if mode == "audio":
        common += [
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "192K",
            "--embed-thumbnail",
            "--add-metadata",
        ]

    else:
        # First choice: MP4/H264 video with audio.
        common += [
            "-f",
            (
                "bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/"
                "b[ext=mp4]/"
                "bv*+ba/"
                "b"
            ),
            "--merge-output-format",
            "mp4",
        ]

    common.append(url)

    return common


async def run_process(command):
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=DOWNLOAD_TIMEOUT,
        )
    except asyncio.TimeoutError:
        try:
            process.kill()
        except Exception:
            pass

        await process.communicate()

        raise TimeoutError(
            "yt-dlp exceeded the maximum download time"
        )

    return (
        process.returncode,
        stdout.decode("utf-8", errors="ignore"),
        stderr.decode("utf-8", errors="ignore"),
    )


def find_downloaded_files(before):
    current = set()

    for path in DOWNLOAD_DIR.iterdir():
        if path.is_file():
            current.add(path)

    new_files = [
        str(path)
        for path in current
        if path not in before
    ]

    return new_files


async def download_media(url, mode):
    """
    Download public media using yt-dlp.
    Returns:
        {
            "success": bool,
            "file": str | None,
            "error": str
        }
    """

    before = set(DOWNLOAD_DIR.iterdir())

    timestamp = int(time.time() * 1000)

    if mode == "audio":
        output = str(
            DOWNLOAD_DIR / f"tojsaver_{timestamp}.%(ext)s"
        )
    else:
        output = str(
            DOWNLOAD_DIR / f"tojsaver_{timestamp}.%(ext)s"
        )

    commands = []

    # Strategy 1 — normal extraction.
    commands.append(
        build_yt_dlp_command(
            url,
            mode,
            output,
        )
    )

    # Strategy 2 — simpler format fallback.
    if mode == "video":
        commands.append(
            [
                "yt-dlp",
                "--no-playlist",
                "--retries",
                "5",
                "--fragment-retries",
                "5",
                "--socket-timeout",
                "30",
                "--merge-output-format",
                "mp4",
                "-f",
                "best[ext=mp4]/best",
                "-o",
                output,
                url,
            ]
        )

    last_error = ""

    async with download_semaphore:

        for index, command in enumerate(commands, start=1):

            logger.info(
                "Download attempt %s for %s",
                index,
                url,
            )

            try:
                return_code, stdout, stderr = await run_process(
                    command
                )

            except Exception as exc:
                last_error = str(exc)
                logger.exception("Download process failed")
                continue

            combined = (stdout + "\n" + stderr).strip()

            logger.info(
                "yt-dlp return code=%s",
                return_code,
            )

            if return_code != 0:
                last_error = combined[-3000:]
                continue

            new_files = find_downloaded_files(before)

            if not new_files:
                last_error = "yt-dlp finished without creating a file"
                continue

            # Choose largest file.
            new_files.sort(
                key=lambda x: Path(x).stat().st_size,
                reverse=True,
            )

            file_path = new_files[0]

            if not Path(file_path).exists():
                last_error = "downloaded file disappeared"
                continue

            size = Path(file_path).stat().st_size

            if size <= 0:
                cleanup_files(new_files)
                last_error = "empty downloaded file"
                continue

            if size > MAX_FILE_SIZE:
                cleanup_files(new_files)

                return {
                    "success": False,
                    "file": None,
                    "error": (
                        f"file is too large: "
                        f"{size / 1024 / 1024:.1f} MB"
                    ),
                }

            return {
                "success": True,
                "file": file_path,
                "error": "",
            }

        return {
            "success": False,
            "file": None,
            "error": last_error[-3000:],
        }


# ============================================================
# DOWNLOAD SESSION
# ============================================================


def set_pending(context, user_id, url):
    context.user_data["pending_url"] = url
    context.user_data["pending_time"] = time.time()


def get_pending(context, user_id):
    url = context.user_data.get("pending_url")
    created = context.user_data.get("pending_time", 0)

    # Pending URL expires after 15 minutes.
    if not url:
        return None

    if time.time() - created > 900:
        context.user_data.pop("pending_url", None)
        context.user_data.pop("pending_time", None)
        return None

    return url


def clear_pending(context):
    context.user_data.pop("pending_url", None)
    context.user_data.pop("pending_time", None)


# ============================================================
# COMMANDS
# ============================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_user(user)

    await update.message.reply_text(
        t(user.id, "welcome"),
        parse_mode="HTML",
        reply_markup=main_keyboard(user.id),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_user(user)

    await update.message.reply_text(
        t(user.id, "help"),
        parse_mode="HTML",
        reply_markup=main_keyboard(user.id),
    )


async def language_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    register_user(user)

    await update.message.reply_text(
        t(user.id, "language"),
        reply_markup=language_keyboard(),
    )


async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    clear_pending(context)

    await update.message.reply_text(
        t(user.id, "cancelled"),
        reply_markup=main_keyboard(user.id),
    )


async def stats_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if ADMIN_ID == 0 or user.id != ADMIN_ID:
        await update.message.reply_text(
            t(user.id, "stats_denied")
        )
        return

    stats = get_statistics()

    text = (
        "📊 <b>TOJSAVER Statistics</b>\n\n"
        f"👥 Users: <b>{stats['users']}</b>\n"
        f"📥 Total downloads: <b>{stats['total']}</b>\n"
        f"✅ Successful: <b>{stats['successful']}</b>\n"
        f"❌ Failed: <b>{stats['failed']}</b>"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# TEXT MESSAGE HANDLER
# ============================================================


async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if not user or not update.message:
        return

    register_user(user)

    text = update.message.text or ""

    url = extract_url(text)

    if not url:
        await update.message.reply_text(
            t(user.id, "invalid"),
            reply_markup=main_keyboard(user.id),
        )
        return

    if not is_supported_url(url):
        await update.message.reply_text(
            t(user.id, "invalid"),
            reply_markup=main_keyboard(user.id),
        )
        return

    platform = detect_platform(url)

    logger.info(
        "Received URL from user=%s platform=%s url=%s",
        user.id,
        platform,
        url,
    )

    set_pending(context, user.id, url)

    await update.message.reply_text(
        t(user.id, "choose"),
        reply_markup=format_keyboard(
            user.id,
            url,
        ),
    )


# ============================================================
# CALLBACK HANDLER
# ============================================================


async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    user = query.from_user

    register_user(user)

    # VERY IMPORTANT:
    # Telegram clients keep showing the button spinner
    # until callback_query.answer() is called.
    try:
        await query.answer()
    except Exception:
        pass

    data = query.data or ""

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    if data == "language":
        await query.edit_message_text(
            t(user.id, "language"),
            reply_markup=language_keyboard(),
        )
        return

    if data.startswith("lang_"):
        language = data.replace("lang_", "", 1)

        if language not in {"tg", "ru", "en"}:
            language = "tg"

        set_language(user.id, language)

        await query.edit_message_text(
            t(user.id, "welcome"),
            parse_mode="HTML",
            reply_markup=main_keyboard(user.id),
        )

        return

    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if data == "help":
        await query.edit_message_text(
            t(user.id, "help"),
            parse_mode="HTML",
            reply_markup=main_keyboard(user.id),
        )
        return

    # --------------------------------------------------------
    # MAIN MENU VIDEO
    # --------------------------------------------------------

    if data == "video":
        await query.edit_message_text(
            t(user.id, "choose"),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎬 Видео",
                            callback_data="download_video",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "❌ Отмена",
                            callback_data="cancel",
                        )
                    ],
                ]
            ),
        )
        return

    # --------------------------------------------------------
    # MAIN MENU AUDIO
    # --------------------------------------------------------

    if data == "audio":
        await query.edit_message_text(
            t(user.id, "choose"),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎵 MP3",
                            callback_data="download_audio",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "❌ Отмена",
                            callback_data="cancel",
                        )
                    ],
                ]
            ),
        )
        return

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    if data == "cancel":
        clear_pending(context)

        await query.edit_message_text(
            t(user.id, "cancelled"),
            reply_markup=main_keyboard(user.id),
        )

        return

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    if data in {
        "download_video",
        "download_audio",
    }:

        url = get_pending(
            context,
            user.id,
        )

        if not url:

            await query.edit_message_text(
                t(user.id, "invalid"),
                reply_markup=main_keyboard(user.id),
            )

            return

        mode = (
            "audio"
            if data == "download_audio"
            else "video"
        )

        platform = detect_platform(url)

        await query.edit_message_text(
            t(user.id, "downloading")
        )

        try:
            await context.bot.send_chat_action(
                chat_id=query.message.chat_id,
                action=ChatAction.UPLOAD_VIDEO
                if mode == "video"
                else ChatAction.UPLOAD_DOCUMENT,
            )
        except Exception:
            pass

        result = await download_media(
            url,
            mode,
        )

        clear_pending(context)

        if not result["success"]:

            record_download(
                user.id,
                platform,
                mode,
                url,
                False,
                result["error"],
            )

            logger.error(
                "Download failed user=%s platform=%s error=%s",
                user.id,
                platform,
                result["error"],
            )

            await query.message.reply_text(
                t(user.id, "error"),
                parse_mode="HTML",
                reply_markup=main_keyboard(user.id),
            )

            return

        file_path = result["file"]

        try:
            await query.message.reply_text(
                t(user.id, "processing")
            )

            if mode == "audio":

                with open(
                    file_path,
                    "rb",
                ) as audio_file:

                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=audio_file,
                        title="TOJSAVER",
                        performer="TOJSAVER",
                        caption=(
                            "🎵 <b>TOJSAVER</b>\n"
                            "🇹🇯 @TojSaverBot"
                        ),
                        parse_mode="HTML",
                    )

            else:

                with open(
                    file_path,
                    "rb",
                ) as video_file:

                    await context.bot.send_video(
                        chat_id=query.message.chat_id,
                        video=video_file,
                        supports_streaming=True,
                        caption=(
                            "🎬 <b>TOJSAVER</b>\n"
                            "🇹🇯 @TojSaverBot"
                        ),
                        parse_mode="HTML",
                    )

            record_download(
                user.id,
                platform,
                mode,
                url,
                True,
            )

            await query.message.reply_text(
                t(user.id, "success"),
                reply_markup=main_keyboard(user.id),
            )

        except Exception as exc:

            logger.exception(
                "Telegram upload failed"
            )

            record_download(
                user.id,
                platform,
                mode,
                url,
                False,
                str(exc),
            )

            await query.message.reply_text(
                t(user.id, "error"),
                reply_markup=main_keyboard(user.id),
            )

        finally:
            cleanup_files([file_path])

        return


# ============================================================
# ERROR HANDLER
# ============================================================


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.exception(
        "Unhandled exception",
        exc_info=context.error,
    )


# ============================================================
# STARTUP
# ============================================================


async def post_init(application: Application):
    init_database()

    cleanup_download_directory()

    logger.info(
        "=========================================="
    )

    logger.info(
        "TOJSAVER V3 STARTING"
    )

    logger.info(
        "Telegram downloader initialized"
    )

    logger.info(
        "Supported: YouTube / Instagram / TikTok"
    )

    logger.info(
        "=========================================="
    )


# ============================================================
# MAIN
# ============================================================


def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Commands
    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "language",
            language_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "cancel",
            cancel_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "stats",
            stats_command,
        )
    )

    # Callback buttons
    application.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    # Text / links
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )

    application.add_error_handler(
        error_handler
    )

    logger.info(
        "Starting Telegram polling..."
    )

    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
