import os
import re
import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv
import requests

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_MACHINE")

DATETIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
NEPAL_TZ = ZoneInfo("Asia/Kathmandu")




def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ New Reminder", callback_data="new_reminder"),
            InlineKeyboardButton("📋 My Reminders", callback_data="list"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
            InlineKeyboardButton("👨‍💻 About", callback_data="about"),
        ],
    ])


def main_menu_text(first_name: str, status_msg: str) -> str:
    return (
        f"Hello, {first_name}! 👋\n\n"
        f"{status_msg}\n\n"
        f"*RemindMe Bot* helps you set reminders right from Telegram.\n\n"
        f"📌 *Quick Usage:*\n"
        f"`/remind Buy milk 2026-03-15T09:00:00`\n"
        f"_All times are in Nepal Time (NPT)_ 🇳🇵\n\n"
        f"Tap a button below to get started 👇"
    )


ABOUT_TEXT = (
    "👨‍💻 *About RemindMe Bot*\n\n"
    "This bot was created by *Umaan Banjara*\n\n"
    "📧 Email: umaanbanjara@gmail.com\n"
    "🐙 GitHub: [UmaanBanjara](https://github.com/UmaanBanjara/)\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "_Feel free to reach out for any issues or suggestions!_"
)

HELP_TEXT = (
    "🤖 *RemindMe Bot — Help*\n\n"
    "*Commands:*\n\n"
    "▶️ /start — Register and open main menu\n\n"
    "⏰ /remind `<message> <YYYY-MM-DDTHH:MM:SS>`\n"
    "   Create a new reminder\n"
    "   ✅ `/remind Call John 2026-03-15T09:00:00`\n"
    "   ✅ `/remind Buy groceries 2026-03-15T18:30:00`\n"
    "   ❌ Do NOT use quotes around the message\n\n"
    "📋 /list — View all your reminders\n\n"
    "🗑 /delete `<id>` — Delete a reminder\n"
    "   Example: `/delete 3`\n\n"
    "❓ /help — Show this message\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🕐 *Date format:* `YYYY-MM-DDTHH:MM:SS`\n"
    "   Example: `2026-03-15T09:00:00`\n"
    "   🇳🇵 *All times are in Nepal Time (NPT)*\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "👨‍💻 *Created by* Umaan Banjara\n"
    "📧 umaanbanjara@gmail.com\n"
    "🐙 [GitHub](https://github.com/UmaanBanjara/)\n\n"
    "_Tip: Use the buttons on /start for quick access!_"
)

NEW_REMINDER_TEXT = (
    "➕ *New Reminder*\n\n"
    "Send your reminder using this format:\n\n"
    "`/remind <message> <YYYY-MM-DDTHH:MM:SS>`\n\n"
    "✅ `/remind Call John 2026-03-15T09:00:00`\n"
    "✅ `/remind Buy groceries 2026-03-20T18:30:00`\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🇳🇵 All times are in *Nepal Time (NPT)*\n"
    "📅 Must be a *future* date and time\n"
    "⛔ Max *30 days* from today\n"
    "❌ Do NOT use quotes around the message"
)




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.message.from_user.id)
    first_name = update.message.from_user.first_name

    try:
        response = requests.post(
            f"{API_URL}/user/create",
            json={"telegram_id": telegram_id},
            timeout=10
        )
        if response.status_code == 201:
            status_msg = "✅ You have been registered!"
        elif response.status_code == 400:
            status_msg = "👋 Welcome back!"
        elif response.status_code == 429:
            status_msg = "⚠️ Too many requests. Please wait a moment."
        else:
            status_msg = "⚠️ Something went wrong. Try again later."
    except requests.exceptions.RequestException:
        status_msg = "⚠️ Could not reach the server. Try again later."

    await update.message.reply_text(
        main_menu_text(first_name, status_msg),
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )




async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏠 Back to Menu", callback_data="start_menu"),
            InlineKeyboardButton("👨‍💻 About", callback_data="about"),
        ]
    ])

    if update.message:
        await update.message.reply_text(HELP_TEXT, parse_mode="Markdown", reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.edit_text(HELP_TEXT, parse_mode="Markdown", reply_markup=keyboard)




async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏠 Back to Menu", callback_data="start_menu"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ]
    ])

    if update.message:
        await update.message.reply_text(ABOUT_TEXT, parse_mode="Markdown", reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.edit_text(ABOUT_TEXT, parse_mode="Markdown", reply_markup=keyboard)



async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.message.from_user.id)

    USAGE = (
        "⚠️ *Wrong usage!*\n\n"
        "*Correct:* `/remind <message> <YYYY-MM-DDTHH:MM:SS>`\n\n"
        "✅ `/remind Call John 2026-03-15T09:00:00`\n"
        "✅ `/remind Buy groceries 2026-03-20T18:30:00`\n\n"
        "🇳🇵 All times are in *Nepal Time (NPT)*\n"
        "❌ Do NOT use quotes around the message\n"
        "❌ Date must be last, in format: `2026-03-15T09:00:00`"
    )

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(USAGE, parse_mode="Markdown")
        return

    args = [a.strip('"\'') for a in context.args]
    scheduled_time = args[-1]
    message = " ".join(args[:-1]).strip()

    if not DATETIME_PATTERN.match(scheduled_time):
        await update.message.reply_text(
            f"❌ *Invalid date format!*\n\n"
            f"You wrote: `{scheduled_time}`\n\n"
            f"✅ Correct format: `2026-03-15T09:00:00`\n"
            f"_(Year-Month-DayTHour:Minute:Second)_",
            parse_mode="Markdown"
        )
        return

    if not message:
        await update.message.reply_text(USAGE, parse_mode="Markdown")
        return

    try:
        reminder_dt_nepal = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M:%S")
        reminder_dt_nepal = reminder_dt_nepal.replace(tzinfo=NEPAL_TZ)
    except ValueError:
        await update.message.reply_text(
            "❌ *Could not parse the date.* Use format: `2026-03-15T09:00:00`",
            parse_mode="Markdown"
        )
        return

    reminder_dt_utc = reminder_dt_nepal.astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)
    max_allowed_utc = now_utc + timedelta(days=30)

    if reminder_dt_utc <= now_utc:
        now_nepal = now_utc.astimezone(NEPAL_TZ)
        await update.message.reply_text(
            f"❌ *That time has already passed!*\n\n"
            f"You entered: `{scheduled_time}` 🇳🇵\n"
            f"Current Nepal time: `{now_nepal.strftime('%Y-%m-%dT%H:%M:%S')}`\n\n"
            f"⏩ Please choose a future date and time.",
            parse_mode="Markdown"
        )
        return

    if reminder_dt_utc > max_allowed_utc:
        max_nepal = max_allowed_utc.astimezone(NEPAL_TZ)
        await update.message.reply_text(
            f"❌ *Too far in the future!*\n\n"
            f"You entered: `{scheduled_time}` 🇳🇵\n"
            f"Maximum allowed: `{max_nepal.strftime('%Y-%m-%dT%H:%M:%S')}` 🇳🇵\n\n"
            f"📅 Reminders can only be set up to *30 days* from today.",
            parse_mode="Markdown"
        )
        return

    scheduled_time_utc = reminder_dt_utc.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        payload = {
            "telegram_id": telegram_id,
            "message": message,
            "scheduled_time": scheduled_time_utc
        }
        response = requests.post(f"{API_URL}/reminder/create", json=payload, timeout=10)

        if response.status_code == 201:
            data = response.json()
            await update.message.reply_text(
                f"✅ *Reminder Created!*\n\n"
                f"🆔 ID: `{data['id']}`\n"
                f"📝 Message: `{message}`\n"
                f"🕐 Time: `{scheduled_time}` 🇳🇵\n\n"
                f"_Use /delete `{data['id']}` to remove it._",
                parse_mode="Markdown"
            )
        elif response.status_code == 409:
            await update.message.reply_text(
                f"⚠️ *Duplicate Reminder!*\n\n"
                f"You already have this reminder scheduled:\n"
                f"📝 `{message}`\n"
                f"🕐 `{scheduled_time}` 🇳🇵\n\n"
                f"Use /list to see all your reminders.",
                parse_mode="Markdown"
            )
        elif response.status_code == 429:
            await update.message.reply_text(
                "⚠️ *Too many requests!*\n\n"
                "You are sending too fast.\n"
                "Please wait a minute and try again. ⏳",
                parse_mode="Markdown"
            )
        elif response.status_code == 404:
            await update.message.reply_text(
                "❌ User not found. Please send /start first."
            )
        else:
            logger.error(f"Reminder create error: {response.status_code} {response.text}")
            await update.message.reply_text(
                f"❌ *Failed to create reminder.*\n\n"
                f"Error `{response.status_code}` — Try again later.",
                parse_mode="Markdown"
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        await update.message.reply_text("❌ Could not reach the server. Try again later.")



async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        telegram_id = str(update.message.from_user.id)
    else:
        telegram_id = str(update.callback_query.from_user.id)

    try:
        response = requests.post(
            f"{API_URL}/reminder/list",
            json={"telegram_id": telegram_id},
            timeout=10
        )

        if response.status_code == 200:
            reminders = response.json()
            if not reminders:
                msg = (
                    "📭 *No reminders found.*\n\n"
                    "Use /remind to create your first one!\n"
                    "Example: `/remind Call John 2026-03-15T09:00:00`"
                )
            else:
                msg = f"📋 *Your Reminders* ({len(reminders)} total)\n"
                msg += "_All times in Nepal Time 🇳🇵_\n\n"
                for r in reminders:
                    status = "✅ Sent" if r['is_sent'] else "⏳ Pending"
                    msg += (
                        f"🔔 *#{r['id']}* — {r['message']}\n"
                        f"   🕐 `{r['scheduled_time']}`\n"
                        f"   {status}\n\n"
                    )
                msg += "_Use /delete `<id>` to remove a reminder._"

        elif response.status_code == 429:
            msg = (
                "⚠️ *Too many requests!*\n\n"
                "You are sending too fast.\n"
                "Please wait a minute and try again. ⏳"
            )
        elif response.status_code == 404:
            msg = "❌ User not found. Please send /start first."
        else:
            logger.error(f"List error: {response.status_code} {response.text}")
            msg = f"❌ *Failed to fetch reminders.*\n\nError `{response.status_code}` — Try again later."

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        msg = "❌ Could not reach the server. Try again later."

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="list"),
            InlineKeyboardButton("🏠 Menu", callback_data="start_menu"),
        ]
    ])

    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.edit_text(msg, parse_mode="Markdown", reply_markup=keyboard)



async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.message.from_user.id)

    try:
        reminder_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text(
            "⚠️ *Usage:* `/delete <reminder_id>`\n"
            "_Example:_ `/delete 3`\n\n"
            "Use /list to see your reminder IDs.",
            parse_mode="Markdown"
        )
        return

    try:
        payload = {"telegram_id": telegram_id, "remainder_id": reminder_id}
        response = requests.post(f"{API_URL}/reminder/delete", json=payload, timeout=10)

        if response.status_code == 200:
            await update.message.reply_text(
                f"🗑 *Reminder #{reminder_id} deleted.*\n\n"
                f"Use /list to see remaining reminders.",
                parse_mode="Markdown"
            )
        elif response.status_code == 429:
            await update.message.reply_text(
                "⚠️ *Too many requests!*\n\n"
                "You are sending too fast.\n"
                "Please wait a minute and try again. ⏳",
                parse_mode="Markdown"
            )
        elif response.status_code == 404:
            await update.message.reply_text(
                f"❌ Reminder `#{reminder_id}` not found.\n"
                f"Use /list to see valid IDs.",
                parse_mode="Markdown"
            )
        else:
            logger.error(f"Delete error: {response.status_code} {response.text}")
            await update.message.reply_text(
                f"❌ *Failed to delete reminder.*\n\n"
                f"Error `{response.status_code}` — Try again later.",
                parse_mode="Markdown"
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        await update.message.reply_text("❌ Could not reach the server. Try again later.")



async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "new_reminder":
        await query.message.edit_text(
            NEW_REMINDER_TEXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Back to Menu", callback_data="start_menu")]
            ]),
            parse_mode="Markdown"
        )
    elif query.data == "help":
        await help_command(update, context)
    elif query.data == "list":
        await list_reminders(update, context)
    elif query.data == "about":
        await about_command(update, context)
    elif query.data == "start_menu":
        first_name = query.from_user.first_name
        await query.message.edit_text(
            main_menu_text(first_name, "What would you like to do?"),
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )



async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Unknown command. Use /help to see all available commands."
    )



async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ I only understand commands!\n\n"
        "Use /help to see all available commands\n"
        "or tap /start to open the main menu.",
    )

if __name__ == "__main__":
    from app.apscheduler.apscheduler_config import start_scheduler

    async def post_init(application):
        start_scheduler(bot=application.bot)

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("list", list_reminders))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Bot is running...")
    app.run_polling()
