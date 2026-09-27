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
# Например:
# ADMIN_ID = 123456789
# =========================================================

ADMIN_ID = 8479464985


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

        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇷🇺 Видео и музыка из социальных сетей.\n\n"
            "📥 Отправь ссылку на Instagram, YouTube или TikTok."
        ),

        "menu": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "Выбери действие:"
        ),

        "choose_format": "📥 <b>Выбери формат:</b>",

        "video": "🎬 Скачать видео",
        "audio": "🎵 Скачать MP3",
        "language": "🌐 Язык",
        "stats": "📊 Моя статистика",
        "admin": "👑 Админ-панель",

        "back": "⬅️ Назад",

        "processing_video": "⏳ Скачиваю видео...",
        "processing_audio": "⏳ Скачиваю музыку...",

        "video_ready": "🎬 Видео готово!",
        "audio_ready": "🎵 Музыка готова!",

        "error": "❌ Не удалось скачать файл.",

        "bad_link": (
            "🔗 Отправь ссылку на Instagram, YouTube или TikTok."
        ),

        "language_title": "🌐 <b>Выбери язык:</b>",
        "language_changed": "✅ Язык изменён.",

        "user_stats": (
            "📊 <b>Твоя статистика</b>\n\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}\n"
            "📥 Всего скачиваний: {total}"
        ),

        "admin_title": (
            "👑 <b>АДМИН-ПАНЕЛЬ TOJSAVER</b>\n\n"
            "Добро пожаловать, администратор."
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

        "admin_only": "⛔ Доступ только для администратора.",

    },


    "tg": {

        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇹🇯 Видео ва мусиқиро аз шабакаҳои иҷтимоӣ зеркашӣ кун.\n\n"
            "📥 Линкаи Instagram, YouTube ё TikTok-ро фирист."
        ),

        "menu": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "Амалро интихоб кун:"
        ),

        "choose_format": "📥 <b>Форматро интихоб кун:</b>",

        "video": "🎬 Зеркашии видео",
        "audio": "🎵 Зеркашии MP3",
        "language": "🌐 Забон",
        "stats": "📊 Статистикаи ман",
        "admin": "👑 Панели админ",

        "back": "⬅️ Бозгашт",

        "processing_video": "⏳ Видео зеркашӣ шуда истодааст...",
        "processing_audio": "⏳ Мусиқӣ зеркашӣ шуда истодааст...",

        "video_ready": "🎬 Видео тайёр!",
        "audio_ready": "🎵 Мусиқӣ тайёр!",

        "error": "❌ Файлро зеркашӣ карда натавонистам.",

        "bad_link": (
            "🔗 Линкаи Instagram, YouTube ё TikTok-ро фирист."
        ),

        "language_title": "🌐 <b>Забонро интихоб кун:</b>",
        "language_changed": "✅ Забон иваз шуд.",

        "user_stats": (
            "📊 <b>Статистикаи ту</b>\n\n"
            "🎬 Видео: {videos}\n"
            "🎵 MP3: {audios}\n"
            "📥 Ҳамаи зеркашиҳо: {total}"
        ),

        "admin_title": (
            "👑 <b>ПАНЕЛИ АДМИНИ TOJSAVER</b>\n\n"
            "Хуш омадед, администратор."
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

        "admin_only": "⛔ Танҳо барои администратор.",

    },


    "en": {

        "welcome": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "🇬🇧 Video and music downloader.\n\n"
            "📥 Send an Instagram, YouTube or TikTok link."
        ),

        "menu": (
            "🎬 <b>TOJSAVER</b>\n\n"
            "Choose an action:"
        ),

        "choose_format": "📥 <b>Choose format:</b>",

        "video": "🎬 Download video",
        "audio": "🎵 Download MP3",
        "language": "🌐 Language",
        "stats": "📊 My statistics",
        "admin": "👑 Admin panel",

        "back": "⬅️ Back",

        "processing_video": "⏳ Downloading video...",
        "processing_audio": "⏳ Downloading music...",

        "video_ready": "🎬 Video ready!",
        "audio_ready": "🎵 Music ready!",

        "error": "❌ Failed to download the file.",

        "bad_link": (
            "🔗 Send an Instagram, YouTube or TikTok link."
        ),

        "language_title": "🌐 <b>Choose language:</b>",
        "language_changed": "✅ Language changed.",

        "user_stats": (
            "📊 <b>Your statistics</b>\n\n"
            "🎬 Videos: {videos}\n"
            "🎵 MP3: {audios}\n"
            "📥 Total downloads: {total}"
        ),

        "admin_title": (
            "👑 <b>TOJSAVER ADMIN PANEL</b>\n\n"
            "Welcome, administrator."
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

        "admin_only": "⛔ Admin access only.",

    }

}


# =========================================================
# LANGUAGE
# =========================================================

def get_lang(context):
    return context.user_data.get("lang", "ru")


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(update: Update):

    user = update.effective_user

    if not user:
        return False

    return user.id == ADMIN_ID


# =========================================================
# REGISTER USER
# =========================================================

def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
        "users": len(data.get("users", set())),
        "downloads": data.get("downloads", 0),
        "videos": data.get("videos", 0),
        "audios": data.get("audios", 0),
    }


def add_download(context, media_type):

    data = context.application.bot_data

    data["downloads"] = data.get("downloads", 0) + 1

    if media_type == "video":

        data["videos"] = data.get("videos", 0) + 1

    elif media_type == "audio":

        data["audios"] = data.get("audios", 0) + 1


# =========================================================
# MAIN KEYBOARD
# =========================================================

def main_keyboard(lang, admin=False):

    t = TEXTS[lang]

    keyboard = [

        [
            InlineKeyboardButton(
                t["video"],
                callback_data="menu_video"
            ),

            InlineKeyboardButton(
                t["audio"],
                callback_data="menu_audio"
            ),
        ],

        [
            InlineKeyboardButton(
                t["stats"],
                callback_data="user_stats"
            ),
        ],

        [
            InlineKeyboardButton(
                t["language"],
                callback_data="language"
            ),
        ],

    ]

    # ADMIN BUTTON ONLY FOR ADMIN
    if admin:

        keyboard.append(
            [
                InlineKeyboardButton(
                    t["admin"],
                    callback_data="admin_panel"
                )
            ]
        )

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# LANGUAGE KEYBOARD
# =========================================================

def language_keyboard():

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
                "⬅️ Назад",
                callback_data="back_main"
            )
        ],

    ])


# =========================================================
# ADMIN KEYBOARD
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    register_user(update, context)

    lang = get_lang(context)

    t = TEXTS[lang]

    await update.message.reply_text(

        t["welcome"],

        parse_mode="HTML",

        reply_markup=main_keyboard(
            lang,
            is_admin(update)
        )

    )


# =========================================================
# ADMIN COMMAND
# =========================================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    register_user(update, context)

    lang = get_lang(context)

    t = TEXTS[lang]

    if not is_admin(update):

        await update.message.reply_text(
            t["admin_only"]
        )

        return

    await update.message.reply_text(

        t["admin_title"],

        parse_mode="HTML",

        reply_markup=admin_keyboard()

    )


# =========================================================
# HANDLE LINK
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

            ]

        ])

    )


# =========================================================
# LANGUAGE MENU
# =========================================================

async def language_menu(update, context):

    query = update.callback_query

    await query.answer()

    lang = get_lang(context)

    t = TEXTS[lang]

    await query.edit_message_text(

        t["language_title"],

        parse_mode="HTML",

        reply_markup=language_keyboard()

    )


# =========================================================
# CHANGE LANGUAGE
# =========================================================

async def change_language(update, context):

    query = update.callback_query

    await query.answer()

    lang = query.data.replace(
        "lang_",
        ""
    )

    context.user_data["lang"] = lang

    t = TEXTS[lang]

    await query.edit_message_text(

        t["language_changed"],

        reply_markup=main_keyboard(
            lang,
            query.from_user.id == ADMIN_ID
        )

    )


# =========================================================
# USER STATISTICS
# =========================================================

async def user_stats(update, context):

    query = update.callback_query

    await query.answer()

    lang = get_lang(context)

    t = TEXTS[lang]

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

        t["user_stats"].format(

            videos=videos,
            audios=audios,
            total=total

        ),

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(
                    t["back"],
                    callback_data="back_main"
                )

            ]

        ])

    )


# =========================================================
# DOWNLOAD MEDIA
# =========================================================

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

    # =====================================================
    # VIDEO
    # =====================================================

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

                await query.edit_message_text(
                    t["video_ready"]
                )

                with open(
                    filename,
                    "rb"
                ) as video:

                    await query.message.reply_video(

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

        except Exception as e:

            print(
                f"VIDEO ERROR: {e}"
            )

            await query.edit_message_text(
                t["error"]
            )


    # =====================================================
    # AUDIO
    # =====================================================

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

                await query.edit_message_text(
                    t["audio_ready"]
                )

                with open(
                    filename,
                    "rb"
                ) as audio:

                    await query.message.reply_audio(

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

        except Exception as e:

            print(
                f"AUDIO ERROR: {e}"
            )

            await query.edit_message_text(
                t["error"]
            )


# =========================================================
# ADMIN PANEL
# =========================================================

async def admin_panel(update, context):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:

        lang = get_lang(context)

        await query.answer(
            TEXTS[lang]["admin_only"],
            show_alert=True
        )

        return

    lang = get_lang(context)

    t = TEXTS[lang]

    await query.edit_message_text(

        t["admin_title"],

        parse_mode="HTML",

        reply_markup=admin_keyboard()

    )


# =========================================================
# ADMIN STATS
# =========================================================

async def admin_stats(update, context):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    lang = get_lang(context)

    t = TEXTS[lang]

    stats = get_global_stats(
        context
    )

    await query.edit_message_text(

        t["admin_stats"].format(
            users=stats["users"],
            downloads=stats["downloads"],
            videos=stats["videos"],
            audios=stats["audios"],
        ),

        parse_mode="HTML",

        reply_markup=admin_keyboard()

    )


# =========================================================
# ADMIN USERS
# =========================================================

async def admin_users(update, context):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    lang = get_lang(context)

    t = TEXTS[lang]

    stats = get_global_stats(
        context
    )

    await query.edit_message_text(

        t["admin_users"].format(
            users=stats["users"]
        ),

        parse_mode="HTML",

        reply_markup=admin_keyboard()

    )


# =========================================================
# ADMIN DOWNLOADS
# =========================================================

async def admin_downloads(update, context):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    lang = get_lang(context)

    t = TEXTS[lang]

    stats = get_global_stats(
        context
    )

    await query.edit_message_text(

        t["admin_downloads"].format(

            downloads=stats["downloads"],

            videos=stats["videos"],

            audios=stats["audios"]

        ),

        parse_mode="HTML",

        reply_markup=admin_keyboard()

    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def callback_handler(update, context):

    query = update.callback_query

    data = query.data

    # LANGUAGE
    if data == "language":

        await language_menu(
            update,
            context
        )

    elif data.startswith("lang_"):

        await change_language(
            update,
            context
        )

    # DOWNLOAD
    elif data in [
        "video",
        "audio"
    ]:

        await download_media(
            update,
            context
        )

    # MAIN MENU VIDEO
    elif data == "menu_video":

        await query.answer()

        lang = get_lang(context)

        t = TEXTS[lang]

        await query.edit_message_text(

            t["choose_format"],

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        t["video"],
                        callback_data="video"
                    )

                ],

                [

                    InlineKeyboardButton(
                        t["back"],
                        callback_data="back_main"
                    )

                ]

            ])

        )

    # MAIN MENU AUDIO
    elif data == "menu_audio":

        await query.answer()

        lang = get_lang(context)

        t = TEXTS[lang]

        await query.edit_message_text(

            t["choose_format"],

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        t["audio"],
                        callback_data="audio"
                    )

                ],

                [

                    InlineKeyboardButton(
                        t["back"],
                        callback_data="back_main"
                    )

                ]

            ])

        )

    # USER STATS
    elif data == "user_stats":

        await user_stats(
            update,
            context
        )

    # ADMIN
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

    # BACK
    elif data == "back_main":

        await query.answer()

        lang = get_lang(context)

        await query.edit_message_text(

            TEXTS[lang]["menu"],

            parse_mode="HTML",

            reply_markup=main_keyboard(

                lang,

                query.from_user.id == ADMIN_ID

            )

        )


# =========================================================
# MAIN
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
            filters.TEXT & ~filters.COMMAND,
            handle_link
        )

    )

    app.add_handler(

        CallbackQueryHandler(
            callback_handler
        )

    )

    print(
        "TOJSAVER PRO запущен!"
    )

    app.run_polling()


if __name__ == "__main__":

    main()
