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


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("BOT_TOKEN")

# =========================================================
# ВСТАВЬ СЮДА СВОЙ TELEGRAM USER ID
# =========================================================

ADMIN_ID = 8479464985


# =========================================================
# SUPPORTED URLS
# =========================================================

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?"
    r"(?:instagram\.com|youtube\.com|youtu\.be|"
    r"tiktok\.com)"
    r"/\S+",
    re.IGNORECASE,
)


# =========================================================
# TEXTS
# =========================================================

TEXTS = {

    "ru": {

        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇷🇺 Видео и музыка из социальных сетей.\n\n"
            "📥 Отправь ссылку на Instagram, YouTube "
            "или TikTok."
        ),

        "menu": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "Выбери действие:"
        ),

        "choose_format": (
            "📥 <b>Выбери формат:</b>"
        ),

        "send_link_video": (
            "🎬 <b>Скачать видео</b>\n\n"
            "🔗 Отправь ссылку на Instagram, "
            "YouTube или TikTok."
        ),

        "send_link_audio": (
            "🎵 <b>Скачать MP3</b>\n\n"
            "🔗 Отправь ссылку на Instagram, "
            "YouTube или TikTok."
        ),

        "video": "🎬 Скачать видео",
        "audio": "🎵 Скачать MP3",
        "language": "🌐 Язык",
        "stats": "📊 Моя статистика",
        "admin": "👑 Админ-панель",

        "back": "⬅️ Назад",

        "processing_video": (
            "⏳ Скачиваю видео...\n\n"
            "Пожалуйста, подожди."
        ),

        "processing_audio": (
            "⏳ Скачиваю музыку...\n\n"
            "Пожалуйста, подожди."
        ),

        "video_ready": "🎬 Видео готово!",
        "audio_ready": "🎵 Музыка готова!",

        "error": (
            "❌ Не удалось скачать файл.\n\n"
            "Попробуй другую ссылку."
        ),

        "bad_link": (
            "🔗 Отправь корректную ссылку на "
            "Instagram, YouTube или TikTok."
        ),

        "language_title": (
            "🌐 <b>Выбери язык:</b>"
        ),

        "language_changed": (
            "✅ Язык изменён."
        ),

        "user_stats": (
            "📊 <b>Твоя статистика</b>\n\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}\n"
            "📥 Всего скачиваний: {total}"
        ),

        "admin_title": (
            "👑 <b>АДМИН-ПАНЕЛЬ TOJSAVER</b>\n\n"
            "Выбери раздел:"
        ),

        "admin_stats": (
            "📊 <b>Статистика TOJSAVER</b>\n\n"
            "👥 Пользователей: {users}\n"
            "📥 Всего скачиваний: {downloads}\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}"
        ),

        "admin_users": (
            "👥 <b>Пользователи</b>\n\n"
            "Всего пользователей: {users}"
        ),

        "admin_downloads": (
            "📥 <b>Скачивания</b>\n\n"
            "Всего: {downloads}\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}"
        ),

        "admin_only": (
            "⛔ Доступ только для администратора."
        ),

    },


    "tg": {

        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇹🇯 Видео ва мусиқиро аз шабакаҳои "
            "иҷтимоӣ зеркашӣ кун.\n\n"
            "📥 Линкаи Instagram, YouTube ё TikTok-ро "
            "фирист."
        ),

        "menu": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "Амалро интихоб кун:"
        ),

        "choose_format": (
            "📥 <b>Форматро интихоб кун:</b>"
        ),

        "send_link_video": (
            "🎬 <b>Зеркашии видео</b>\n\n"
            "🔗 Линкаи Instagram, YouTube ё TikTok-ро "
            "фирист."
        ),

        "send_link_audio": (
            "🎵 <b>Зеркашии MP3</b>\n\n"
            "🔗 Линкаи Instagram, YouTube ё TikTok-ро "
            "фирист."
        ),

        "video": "🎬 Зеркашии видео",
        "audio": "🎵 Зеркашии MP3",
        "language": "🌐 Забон",
        "stats": "📊 Статистикаи ман",
        "admin": "👑 Панели админ",

        "back": "⬅️ Бозгашт",

        "processing_video": (
            "⏳ Видео зеркашӣ шуда истодааст...\n\n"
            "Лутфан интизор шав."
        ),

        "processing_audio": (
            "⏳ Мусиқӣ зеркашӣ шуда истодааст...\n\n"
            "Лутфан интизор шав."
        ),

        "video_ready": "🎬 Видео тайёр!",
        "audio_ready": "🎵 Мусиқӣ тайёр!",

        "error": (
            "❌ Файлро зеркашӣ карда натавонистам.\n\n"
            "Линкаи дигарро санҷ."
        ),

        "bad_link": (
            "🔗 Линкаи дурусти Instagram, YouTube ё "
            "TikTok-ро фирист."
        ),

        "language_title": (
            "🌐 <b>Забонро интихоб кун:</b>"
        ),

        "language_changed": (
            "✅ Забон иваз шуд."
        ),

        "user_stats": (
            "📊 <b>Статистикаи ту</b>\n\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}\n"
            "📥 Ҳамаи зеркашиҳо: {total}"
        ),

        "admin_title": (
            "👑 <b>ПАНЕЛИ АДМИНИ TOJSAVER</b>\n\n"
            "Қисмро интихоб кун:"
        ),

        "admin_stats": (
            "📊 <b>Статистикаи TOJSAVER</b>\n\n"
            "👥 Истифодабарандагон: {users}\n"
            "📥 Ҳамаи зеркашиҳо: {downloads}\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}"
        ),

        "admin_users": (
            "👥 <b>Истифодабарандагон</b>\n\n"
            "Ҳама: {users}"
        ),

        "admin_downloads": (
            "📥 <b>Зеркашиҳо</b>\n\n"
            "Ҳама: {downloads}\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}"
        ),

        "admin_only": (
            "⛔ Танҳо барои администратор."
        ),

    },


    "en": {

        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇬🇧 Video and music downloader.\n\n"
            "📥 Send an Instagram, YouTube or "
            "TikTok link."
        ),

        "menu": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "Choose an action:"
        ),

        "choose_format": (
            "📥 <b>Choose format:</b>"
        ),

        "send_link_video": (
            "🎬 <b>Download video</b>\n\n"
            "🔗 Send an Instagram, YouTube or "
            "TikTok link."
        ),

        "send_link_audio": (
            "🎵 <b>Download MP3</b>\n\n"
            "🔗 Send an Instagram, YouTube or "
            "TikTok link."
        ),

        "video": "🎬 Download video",
        "audio": "🎵 Download MP3",
        "language": "🌐 Language",
        "stats": "📊 My statistics",
        "admin": "👑 Admin panel",

        "back": "⬅️ Back",

        "processing_video": (
            "⏳ Downloading video...\n\n"
            "Please wait."
        ),

        "processing_audio": (
            "⏳ Downloading music...\n\n"
            "Please wait."
        ),

        "video_ready": "🎬 Video ready!",
        "audio_ready": "🎵 Music ready!",

        "error": (
            "❌ Failed to download the file.\n\n"
            "Try another link."
        ),

        "bad_link": (
            "🔗 Send a valid Instagram, YouTube or "
            "TikTok link."
        ),

        "language_title": (
            "🌐 <b>Choose language:</b>"
        ),

        "language_changed": (
            "✅ Language changed."
        ),

        "user_stats": (
            "📊 <b>Your statistics</b>\n\n"
            "🎬 Videos: {videos}\n"
            "🎵 MP3: {audios}\n"
            "📥 Total downloads: {total}"
        ),

        "admin_title": (
            "👑 <b>TOJSAVER ADMIN PANEL</b>\n\n"
            "Choose a section:"
        ),

        "admin_stats": (
            "📊 <b>TOJSAVER Statistics</b>\n\n"
            "👥 Users: {users}\n"
            "📥 Total downloads: {downloads}\n"
            "🎬 Videos: {videos}\n"
            "🎵 MP3: {audios}"
        ),

        "admin_users": (
            "👥 <b>Users</b>\n\n"
            "Total users: {users}"
        ),

        "admin_downloads": (
            "📥 <b>Downloads</b>\n\n"
            "Total: {downloads}\n"
            "🎬 Videos: {videos}\n"
            "🎵 MP3: {audios}"
        ),

        "admin_only": (
            "⛔ Admin access only."
        ),

    }

}


# =========================================================
# LANGUAGE
# =========================================================

def get_lang(context):

    return context.user_data.get(
        "lang",
        "ru"
    )


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(update):

    user = update.effective_user

    if not user:
        return False

    return user.id == ADMIN_ID


# =========================================================
# REGISTER USER
# =========================================================

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
# GLOBAL STATS
# =========================================================

def get_global_stats(context):

    data = context.application.bot_data

    return {
        "users": len(
            data.get("users", set())
        ),

        "downloads": data.get(
            "downloads",
            0
        ),

        "videos": data.get(
            "videos",
            0
        ),

        "audios": data.get(
            "audios",
            0
        ),
    }


def add_download(context, media_type):

    data = context.application.bot_data

    data["downloads"] = (
        data.get("downloads", 0) + 1
    )

    if media_type == "video":

        data["videos"] = (
            data.get("videos", 0) + 1
        )

    elif media_type == "audio":

        data["audios"] = (
            data.get("audios", 0) + 1
        )


# =========================================================
# MAIN KEYBOARD
# =========================================================

def main_keyboard(lang, admin=False):

    t = TEXTS[lang]

    keyboard = [

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

        keyboard.append(
            [
                InlineKeyboardButton(
                    t["admin"],
                    callback_data="admin_panel"
                )
            ]
        )

    return InlineKeyboardMarkup(
        keyboard
    )


# =========================================================
# BACK BUTTON
# =========================================================

def back_keyboard(lang):

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                TEXTS[lang]["back"],
                callback_data="back_main"
            )
        ]

    ])


# =========================================================
# LANGUAGE KEYBOARD
# =========================================================

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
        ],

    ])


# =========================================================
# ADMIN KEYBOARD
# =========================================================

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
                "⬅️ Главное меню",
                callback_data="back_main"
            )
        ],

    ])


# =========================================================
# START
# =========================================================

async def start(update, context):

    register_user(
        update,
        context
    )

    lang = get_lang(context)

    text = TEXTS[lang]["welcome"]

    keyboard = main_keyboard(
        lang,
        is_admin(update)
    )

    chat_id = update.effective_chat.id

    # Удаляем сообщение /start,
    # чтобы оно не засоряло чат
    try:

        await update.message.delete()

    except Exception:
        pass

    # Проверяем, есть ли уже главное меню
    menu_message_id = context.user_data.get(
        "menu_message_id"
    )

    if menu_message_id:

        try:

            await context.bot.edit_message_text(

                chat_id=chat_id,

                message_id=menu_message_id,

                text=text,

                parse_mode="HTML",

                reply_markup=keyboard

            )

            return

        except Exception:

            context.user_data.pop(
                "menu_message_id",
                None
            )

    # Если старого меню нет —
    # создаём новое
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
# ADMIN COMMAND
# =========================================================

async def admin_command(update, context):

    register_user(
        update,
        context
    )

    lang = get_lang(context)

    if not is_admin(update):

        await update.message.reply_text(
            TEXTS[lang]["admin_only"]
        )

        return

    await update.message.reply_text(

        TEXTS[lang]["admin_title"],

        parse_mode="HTML",

        reply_markup=admin_keyboard(
            lang
        )

    )


# =========================================================
# HANDLE LINK
# =========================================================

async def handle_link(update, context):

    register_user(
        update,
        context
    )

    lang = get_lang(context)

    text = update.message.text.strip()

    match = URL_PATTERN.search(text)

    if not match:

        await update.message.reply_text(
            TEXTS[lang]["bad_link"]
        )

        return

    url = match.group(0)

    context.user_data["url"] = url

    mode = context.user_data.get(
        "download_mode"
    )

    # Если пользователь заранее выбрал видео
    if mode == "video":

        context.user_data.pop(
            "download_mode",
            None
        )

        await download_video(
            update,
            context,
            url
        )

        return

    # Если пользователь заранее выбрал MP3
    if mode == "audio":

        context.user_data.pop(
            "download_mode",
            None
        )

        await download_audio(
            update,
            context,
            url
        )

        return

    # Если просто отправил ссылку
    await update.message.reply_text(

        TEXTS[lang]["choose_format"],

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    TEXTS[lang]["video"],
                    callback_data="download_video"
                )

            ],

            [

                InlineKeyboardButton(
                    TEXTS[lang]["audio"],
                    callback_data="download_audio"
                )

            ],

            [

                InlineKeyboardButton(
                    TEXTS[lang]["back"],
                    callback_data="back_main"
                )

            ],

        ])

    )


# =========================================================
# DOWNLOAD VIDEO
# =========================================================

async def download_video(
    update,
    context,
    url
):

    lang = get_lang(context)

    status = await update.effective_chat.send_message(
        TEXTS[lang]["processing_video"]
    )

    try:

        with tempfile.TemporaryDirectory() as temp_dir:

            output = os.path.join(
                temp_dir,
                "%(title).80s.%(ext)s"
            )

            options = {

                "outtmpl": output,

                "format": (
                    "best[ext=mp4]/"
                    "best"
                ),

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

                filename = ydl.prepare_filename(
                    info
                )

            if not os.path.exists(filename):

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
                TEXTS[lang]["video_ready"]
            )

            with open(
                filename,
                "rb"
            ) as video:

                await update.effective_chat.send_video(

                    video=video,

                    caption="🎬 TOJSAVER"

                )

            # USER STATS
            context.user_data["videos"] = (
                context.user_data.get(
                    "videos",
                    0
                ) + 1
            )

            # GLOBAL STATS
            add_download(
                context,
                "video"
            )

    except Exception as error:

        print(
            "VIDEO ERROR:",
            error
        )

        try:

            await status.edit_text(
                TEXTS[lang]["error"]
            )

        except Exception:
            pass


# =========================================================
# DOWNLOAD AUDIO
# =========================================================

async def download_audio(
    update,
    context,
    url
):

    lang = get_lang(context)

    status = await update.effective_chat.send_message(
        TEXTS[lang]["processing_audio"]
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

                filename = (
                    os.path.splitext(
                        filename
                    )[0]
                    + ".mp3"
                )

            if not os.path.exists(filename):

                raise FileNotFoundError()

            await status.edit_text(
                TEXTS[lang]["audio_ready"]
            )

            with open(
                filename,
                "rb"
            ) as audio:

                await update.effective_chat.send_audio(

                    audio=audio,

                    caption="🎵 TOJSAVER"

                )

            # USER STATS
            context.user_data["audios"] = (
                context.user_data.get(
                    "audios",
                    0
                ) + 1
            )

            # GLOBAL STATS
            add_download(
                context,
                "audio"
            )

    except Exception as error:

        print(
            "AUDIO ERROR:",
            error
        )

        try:

            await status.edit_text(
                TEXTS[lang]["error"]
            )

        except Exception:
            pass


# =========================================================
# USER STATISTICS
# =========================================================

async def show_user_stats(
    query,
    context
):

    lang = get_lang(context)

    videos = context.user_data.get(
        "videos",
        0
    )

    audios = context.user_data.get(
        "audios",
        0
    )

    total = videos + audios

    await query.edit_message_text(

        TEXTS[lang]["user_stats"].format(

            videos=videos,

            audios=audios,

            total=total

        ),

        parse_mode="HTML",

        reply_markup=back_keyboard(
            lang
        )

    )


# =========================================================
# ADMIN PANEL
# =========================================================

async def show_admin_panel(
    query,
    context
):

    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "⛔ Access denied",
            show_alert=True
        )

        return

    lang = get_lang(context)

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

    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "⛔ Access denied",
            show_alert=True
        )

        return

    lang = get_lang(context)

    stats = get_global_stats(
        context
    )

    await query.edit_message_text(

        TEXTS[lang]["admin_stats"].format(

            users=stats["users"],

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
# ADMIN USERS
# =========================================================

async def show_admin_users(
    query,
    context
):

    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "⛔ Access denied",
            show_alert=True
        )

        return

    lang = get_lang(context)

    stats = get_global_stats(
        context
    )

    await query.edit_message_text(

        TEXTS[lang]["admin_users"].format(

            users=stats["users"]

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

    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "⛔ Access denied",
            show_alert=True
        )

        return

    lang = get_lang(context)

    stats = get_global_stats(
        context
    )

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
# CALLBACK HANDLER
# =========================================================

async def callback_handler(
    update,
    context
):

    query = update.callback_query

    await query.answer()

    data = query.data

    lang = get_lang(context)

    # -----------------------------------------------------
    # VIDEO BUTTON
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
    # AUDIO BUTTON
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
    # DOWNLOAD VIDEO AFTER URL
    # -----------------------------------------------------

    if data == "download_video":

        url = context.user_data.get(
            "url"
        )

        if not url:

            await query.edit_message_text(
                TEXTS[lang]["bad_link"]
            )

            return

        await query.edit_message_text(
            TEXTS[lang]["processing_video"]
        )

        try:

            with tempfile.TemporaryDirectory() as temp_dir:

                output = os.path.join(
                    temp_dir,
                    "%(title).80s.%(ext)s"
                )

                options = {

                    "outtmpl": output,

                    "format": (
                        "best[ext=mp4]/best"
                    ),

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

                    raise FileNotFoundError()

                await query.edit_message_text(
                    TEXTS[lang]["video_ready"]
                )

                with open(
                    filename,
                    "rb"
                ) as video:

                    await query.message.reply_video(
                        video=video,
                        caption="🎬 TOJSAVER"
                    )

                context.user_data["videos"] = (
                    context.user_data.get(
                        "videos",
                        0
                    ) + 1
                )

                add_download(
                    context,
                    "video"
                )

        except Exception as error:

            print(
                "VIDEO CALLBACK ERROR:",
                error
            )

            await query.edit_message_text(
                TEXTS[lang]["error"]
            )

        return

    # -----------------------------------------------------
    # DOWNLOAD AUDIO AFTER URL
    # -----------------------------------------------------

    if data == "download_audio":

        url = context.user_data.get(
            "url"
        )

        if not url:

            await query.edit_message_text(
                TEXTS[lang]["bad_link"]
            )

            return

        await query.edit_message_text(
            TEXTS[lang]["processing_audio"]
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
                    TEXTS[lang]["audio_ready"]
                )

                with open(
                    filename,
                    "rb"
                ) as audio:

                    await query.message.reply_audio(
                        audio=audio,
                        caption="🎵 TOJSAVER"
                    )

                context.user_data["audios"] = (
                    context.user_data.get(
                        "audios",
                        0
                    ) + 1
                )

                add_download(
                    context,
                    "audio"
                )

        except Exception as error:

            print(
                "AUDIO CALLBACK ERROR:",
                error
            )

            await query.edit_message_text(
                TEXTS[lang]["error"]
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

        new_lang = data.replace(
            "lang_",
            ""
        )

        context.user_data[
            "lang"
        ] = new_lang

        await query.edit_message_text(

            TEXTS[new_lang]["menu"],

            parse_mode="HTML",

            reply_markup=main_keyboard(

                new_lang,

                query.from_user.id == ADMIN_ID

            )

        )

        return

    # -----------------------------------------------------
    # USER STATS
    # -----------------------------------------------------

    if data == "user_stats":

        await show_user_stats(
            query,
            context
        )

        return

    # -----------------------------------------------------
    # ADMIN PANEL
    # -----------------------------------------------------

    if data == "admin_panel":

        await show_admin_panel(
            query,
            context
        )

        return

    # -----------------------------------------------------
    # ADMIN STATS
    # -----------------------------------------------------

    if data == "admin_stats":

        await show_admin_stats(
            query,
            context
        )

        return

    # -----------------------------------------------------
    # ADMIN USERS
    # -----------------------------------------------------

    if data == "admin_users":

        await show_admin_users(
            query,
            context
        )

        return

    # -----------------------------------------------------
    # ADMIN DOWNLOADS
    # -----------------------------------------------------

    if data == "admin_downloads":

        await show_admin_downloads(
            query,
            context
        )

        return

    # -----------------------------------------------------
    # BACK TO MAIN
    # -----------------------------------------------------

    if data == "back_main":

        # Сбрасываем режим скачивания
        context.user_data.pop(
            "download_mode",
            None
        )

        await query.edit_message_text(

            TEXTS[lang]["menu"],

            parse_mode="HTML",

            reply_markup=main_keyboard(

                lang,

                query.from_user.id == ADMIN_ID

            )

        )

        # Запоминаем это сообщение
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
        "BOT ERROR:",
        context.error
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if not TOKEN:

        raise RuntimeError(
            "BOT_TOKEN не найден в GitHub Secrets"
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
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

    # Text messages / links
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link
        )
    )

    # Buttons
    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    # Errors
    app.add_error_handler(
        error_handler
    )

    print(
        "================================"
    )

    print(
        "TOJSAVER PRO STARTED"
    )

    print(
        "================================"
    )

    app.run_polling()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()
