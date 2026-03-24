import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# ── Course Catalogue ──────────────────────────────────────────────────────────
COURSES = {
    "course_1": {
        "name": "UI/UX Design Master Class",
        "price": 100,
        "payment_link": "https://checkout.fapshi.com/link/47655503",
        "course_link": "https://youtu.be/WTNvRAtyZls?si=T3B8kA6yJuK3ctNI",
    },
    "course_2": {
        "name": "Learn JavaScript Basics (Beginners Guide To Frontend JS)",
        "price": 100,
        "payment_link": "https://checkout.fapshi.com/link/92010930",
        "course_link": "https://youtu.be/h-eJdvTRtjk?si=YkYnlZj3MArnFOxP",
    },
}

# Tracks which course a user last selected  {user_id: course_key}
user_selected_course: dict = {}


# ── /start ────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome = (
        " *Welcome to Fly Bot!* \n\n"
        "We're glad to have you here. Whether you're looking to learn something new, "
        "check the weather, or just have a laugh — Fly Bot has you covered.\n\n"
        "Here's what I can do for you:\n\n"
        "   /courses  — Browse & enroll in available courses\n"
        "   /weather  — Get current weather for any city\n"
        "   /joke     — Hear a random joke\n"
       # "   /ask      — Ask Claude anything\n"
        "   /help     — Show this message\n\n"
        "_Choose a command and let's get started!_"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


# ── /help ─────────────────────────────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


# ── /courses — show inline buttons ───────────────────────────────────────────
async def courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(
            f"{info['name']}  •  ${info['price']}",
            callback_data=key
        )]
        for key, info in COURSES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "*Available Courses*\n\nTap a course to see details and get the payment link:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── Inline button handler — user picks a course ───────────────────────────────
async def course_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    course_key = query.data
    if course_key not in COURSES:
        await query.edit_message_text(" Course not found. Please try /courses again.")
        return

    course = COURSES[course_key]
    user_id = query.from_user.id
    user_selected_course[user_id] = course_key

    msg = (
        f" *{course['name']}*\n\n"
        f" Price: *${course['price']}*\n\n"
        f"To enroll, complete your payment using the link below:\n"
        f" [Pay Now]({course['payment_link']})\n\n"
        f"Once payment is done, *send a screenshot or photo of your payment proof* "
        f"here and I'll unlock your course link right away! "
    )
    await query.edit_message_text(msg, parse_mode="Markdown")


# ── Photo handler — user sends payment proof ──────────────────────────────────
async def payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    course_key = user_selected_course.get(user_id)

    if not course_key or course_key not in COURSES:
        await update.message.reply_text(
            " I'm not sure which course you're paying for.\n"
            "Please use /courses to select a course first, then send your payment proof."
        )
        return

    course = COURSES[course_key]

    await update.message.reply_text(
        f" *Payment proof received! Thank you!*\n\n"
        f"Here is your access link for *{course['name']}*:\n\n"
        f" {course['course_link']}\n\n"
        f"Enjoy your course and happy learning! ",
        parse_mode="Markdown",
    )

    del user_selected_course[user_id]


# ── /weather <city> ───────────────────────────────────────────────────────────
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /weather <city>  e.g. /weather Amsterdam")
        return

    city = " ".join(context.args)
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
    )

    try:
        data = requests.get(url, timeout=10).json()
        if data.get("cod") != 200:
            await update.message.reply_text(f" City not found: {city}")
            return

        desc     = data["weather"][0]["description"].capitalize()
        temp     = data["main"]["temp"]
        feels    = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        country  = data["sys"]["country"]

        await update.message.reply_text(
            f"🌤 Weather in {city.title()}, {country}:\n"
            f"  • {desc}\n"
            f"  • Temperature: {temp}°C (feels like {feels}°C)\n"
            f"  • Humidity: {humidity}%"
        )
    except Exception as e:
        await update.message.reply_text(f" Could not fetch weather: {e}")


# ── /joke ─────────────────────────────────────────────────────────────────────
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = requests.get(
            "https://official-joke-api.appspot.com/random_joke", timeout=10
        ).json()
        await update.message.reply_text(f"{data['setup']}\n\n{data['punchline']}")
    except Exception as e:
        await update.message.reply_text(f"Could not fetch a joke: {e}")


# ── /ask <question> ───────────────────────────────────────────────────────────
# async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "YOUR_ANTHROPIC_API_KEY":
#         await update.message.reply_text(
#             " The /ask command isn't configured yet.\n"
#             "Add your ANTHROPIC_API_KEY to enable it."
#         )
#         return

#     if not context.args:
#         await update.message.reply_text("Usage: /ask <your question>  e.g. /ask What is the speed of light?")
#         return

#     question = " ".join(context.args)
#     await update.message.reply_text(" Thinking...")

#     try:
#         response = requests.post(
#             "https://api.anthropic.com/v1/messages",
#             headers={
#                 "x-api-key": ANTHROPIC_API_KEY,
#                 "anthropic-version": "2023-06-01",
#                 "content-type": "application/json",
#             },
#             json={
#                 "model": "claude-sonnet-4-20250514",
#                 "max_tokens": 1024,
#                 "messages": [{"role": "user", "content": question}],
#             },
#             timeout=30,
#         )
#         result = response.json()
#         answer = result["content"][0]["text"]
#         await update.message.reply_text(f" {answer}")
#     except Exception as e:
#         await update.message.reply_text(f" Error contacting Claude: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("help",    help_command))
    app.add_handler(CommandHandler("courses", courses))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("joke",    joke))
    # app.add_handler(CommandHandler("ask",     ask))

    app.add_handler(CallbackQueryHandler(course_selected))
    app.add_handler(MessageHandler(filters.PHOTO, payment_proof))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()