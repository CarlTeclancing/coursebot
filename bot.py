import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# ── General payment link for multi-course orders ──────────────────────────────
BUNDLE_PAYMENT_LINK = "https://checkout.fapshi.com/link/07010939"

# ── Course Catalogue ──────────────────────────────────────────────────────────
COURSES = {
    "1": {
        "name": "► learn figma design in 50 minutes",
        "price": "5000 FCFA",
        "description": "Are you ready to learn how to design in Figma in just 50 minutes? In this video, I'm going to be taking you through everything you need to know about Figma - including an introduction to the platform and a whole lot more. I'll walk through the essential design tools and features, teaching you how you can use them effectively. Along the way, I'll provide tips and tricks on how to create amazing designs using Figma with minimal effort.",
        "link": "https://youtu.be/GWoCNLM3uM0?si=U2jph7GQmkzrwZ7x",
        "payment_link": "https://checkout.fapshi.com/link/36584746",
    },
    "2": {
        "name": "► Learn JavaScript from Scratch",
        "price": "7000 FCFA",
        "description": "Beginner-Friendly Guide to JavaScript! Learn JavaScript from the fundamentals, perfect for beginners who want to start coding. Whether you're building websites, web apps, or getting into front-end development, this guide will help you get started with CODEwithCREST.",
        "link": "https://youtu.be/t-xj8qlf8AA?si=qXT_NAYN_dICDnRu",
        "payment_link": "https://checkout.fapshi.com/link/92010930",
    },
    "3": {
        "name": "► React JS Fundamentals for Beginners",
        "price": "10000 FCFA",
        "description": "Master HTML, CSS, JavaScript, and React. Build professional websites and web applications from scratch.",
        "link": "https://youtu.be/t-xj8qlf8AA?si=pv2y62Z3JbztfzVX",
        "payment_link": "https://checkout.fapshi.com/link/90280853",
    },
    "4": {
        "name": "► HTML For Beginners - Build Your First Website",
        "price": "8000 FCFA",
        "description": "Welcome to the ultimate coding journey! In this video, we delve into the fascinating world of HTML for beginners, offering a comprehensive introduction to the essentials of web development. Whether you're a coding novice or looking to strengthen your skills, join us as we unravel the mysteries of HTML and explore the foundations of CSS.",
        "link": "https://youtu.be/El_XZcT3fAk?si=AgBi6oPU2LInsVq8",
        "payment_link": "https://checkout.fapshi.com/link/13735938",
    },
    "5": {
        "name": "► Roadmap to Learning UI/UX Design in 6 Months",
        "price": "6000 FCFA",
        "description": "Join us as we guide you through each month of this transformative learning journey. From mastering design principles and tools to conducting user research and analysis, creating wireframes and prototypes, diving into visual design and branding, exploring interaction design and animation, and ultimately building a stellar portfolio.",
        "link": "https://youtu.be/WTNvRAtyZls?si=DiIBWgS0m_JxQZ2g",
        "payment_link": "https://checkout.fapshi.com/link/47655503",
    },
}


def get_price_int(course: dict) -> int:
    """Extract integer price from a course dict."""
    try:
        return int(course["price"].split()[0])
    except (ValueError, IndexError):
        return 0


# ── /start — HOME PAGE ────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(" View Courses", callback_data="view_courses")],
        [InlineKeyboardButton(" My Orders",    callback_data="my_orders")],
    ]
    welcome = (
        "► *Welcome to CourseBot Store*\n\n"
        "Your one-stop shop for premium digital courses.\n"
        "Browse, buy, and get instant access to your courses!\n\n"
        "What would you like to do?"
    )
    await update.message.reply_text(
        welcome,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ── VIEW COURSES LIST ─────────────────────────────────────────────────────────
async def view_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(f"{info['name']} • {info['price']}", callback_data=f"course_{cid}")]
        for cid, info in COURSES.items()
    ]
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_home")])
    message = "* Available Courses*\n\nSelect a course to view details:"

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ── COURSE DETAILS PAGE ───────────────────────────────────────────────────────
async def show_course_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    course_id = query.data.split("_")[1]
    if course_id not in COURSES:
        await query.edit_message_text(" Course not found.")
        return

    course = COURSES[course_id]
    message = (
        f"*{course['name']}*\n\n"
        f"*Price:* {course['price']}\n\n"
        f"ℹ️ *Description:*\n{course['description']}\n"
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Add to Cart", callback_data=f"add_to_cart_{course_id}")],
        [InlineKeyboardButton("« Back",         callback_data="view_courses")],
    ]
    await query.edit_message_text(
        message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ── ADD TO CART ───────────────────────────────────────────────────────────────
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    course_id = query.data.split("_")[3]
    if course_id not in COURSES:
        await query.answer(" Course not found.", show_alert=True)
        return

    if "cart" not in context.user_data:
        context.user_data["cart"] = []

    if course_id not in context.user_data["cart"]:
        context.user_data["cart"].append(course_id)
        await query.answer("✓ Course added to cart!", show_alert=True)
    else:
        await query.answer("Already in your cart!", show_alert=True)

    await show_cart(update, context)


# ── SHOW CART ─────────────────────────────────────────────────────────────────
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    cart_items = context.user_data.get("cart", [])

    if not cart_items:
        message = "🛒 *Your Cart is Empty*\n\nBrowse courses and add them to your cart!"
        keyboard = [[InlineKeyboardButton(" Continue Shopping", callback_data="view_courses")]]
    else:
        total_price = sum(get_price_int(COURSES[cid]) for cid in cart_items if cid in COURSES)
        cart_text = "🛒 *Your Shopping Cart*\n\n"
        for idx, cid in enumerate(cart_items, 1):
            if cid in COURSES:
                cart_text += f"{idx}. {COURSES[cid]['name']}\n   {COURSES[cid]['price']}\n\n"
        cart_text += f"*Total: {total_price} FCFA*"
        message = cart_text

        keyboard = [
            [InlineKeyboardButton(f"✗ Remove: {COURSES[cid]['name']}", callback_data=f"remove_from_cart_{cid}")]
            for cid in cart_items if cid in COURSES
        ]
        keyboard.append([InlineKeyboardButton(" Proceed to Checkout", callback_data="checkout")])
        keyboard.append([InlineKeyboardButton("+ Add More Courses",     callback_data="view_courses")])

    if query:
        await query.edit_message_text(
            message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ── REMOVE FROM CART ──────────────────────────────────────────────────────────
async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    course_id = query.data.split("_")[3]

    if "cart" in context.user_data and course_id in context.user_data["cart"]:
        context.user_data["cart"].remove(course_id)
        await query.answer("✓ Course removed from cart!", show_alert=True)
    else:
        await query.answer()

    await show_cart(update, context)


# ── CHECKOUT PAGE ─────────────────────────────────────────────────────────────
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    cart_items = context.user_data.get("cart", [])
    if not cart_items:
        await query.edit_message_text(" Your cart is empty!")
        return

    total_price = sum(get_price_int(COURSES[cid]) for cid in cart_items if cid in COURSES)
    course_list = ""
    for idx, cid in enumerate(cart_items, 1):
        if cid in COURSES:
            course_list += f"{idx}. {COURSES[cid]['name']} — {COURSES[cid]['price']}\n"

    # ── Single course → its own payment link
    # ── Multiple courses → one combined bundle link
    if len(cart_items) == 1:
        cid = cart_items[0]
        payment_link = COURSES[cid]["payment_link"]
        payment_note = f" [Pay {total_price} FCFA]({payment_link})"
    else:
        payment_link = BUNDLE_PAYMENT_LINK
        payment_note = (
            f" [Pay {total_price} FCFA (Bundle)]({payment_link})\n\n"
            f" _Please enter exactly *{total_price} FCFA* on the payment page._"
        )

    message = (
        f"* Payment Summary*\n\n"
        f"*Courses:*\n{course_list}\n"
        f"*Total: {total_price} FCFA*\n\n"
        f"*Payment Link:*\n{payment_note}\n\n"
        f"*Steps:*\n"
        f"1. Click the payment link above\n"
        f"2. Complete the payment\n"
        f"3. Take a screenshot of the confirmation\n"
        f"4. Send the screenshot here\n\n"
        f"You'll get instant access to your courses once proof is received! "
    )

    keyboard = [
        [InlineKeyboardButton("✓ I Have Paid",   callback_data="paid")],
        [InlineKeyboardButton("« Back to Cart",  callback_data="view_cart")],
    ]
    await query.edit_message_text(
        message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ── PAYMENT PROOF REQUEST ─────────────────────────────────────────────────────
async def ask_for_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    message = (
        "* Upload Payment Screenshot*\n\n"
        "Send a photo of your payment confirmation and your courses will be unlocked instantly!"
    )
    keyboard = [[InlineKeyboardButton("« Back to Cart", callback_data="view_cart")]]
    await query.edit_message_text(
        message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ── AUTO DELIVERY ON PHOTO UPLOAD ─────────────────────────────────────────────
async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cart_items = context.user_data.get("cart", [])

    if not cart_items:
        await update.message.reply_text(
            " *No courses in cart.*\n\nUse /start to browse and add courses first.",
            parse_mode="Markdown",
        )
        return

    delivery_message = " *Payment Received! Thank you!*\n\n*Here are your courses:*\n\n"
    for cid in cart_items:
        if cid in COURSES:
            course = COURSES[cid]
            delivery_message += f"*{course['name']}*\n🔗 {course['link']}\n\n"
    delivery_message += "Enjoy your courses and happy learning! "

    await update.message.reply_text(delivery_message, parse_mode="Markdown")

    # Clear cart after delivery
    context.user_data.pop("cart", None)


# ── MY ORDERS ─────────────────────────────────────────────────────────────────
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    message = (
        " *My Orders*\n\n"
        "You haven't purchased any courses yet.\n\n"
        "Browse our courses to get started!"
    )
    keyboard = [
        [InlineKeyboardButton("View Courses", callback_data="view_courses")],
        [InlineKeyboardButton("« Back",          callback_data="back_home")],
    ]
    await query.edit_message_text(
        message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ── BACK TO HOME ──────────────────────────────────────────────────────────────
async def back_to_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("View Courses", callback_data="view_courses")],
        [InlineKeyboardButton("My Orders",    callback_data="my_orders")],
    ]
    welcome = (
        "► *Welcome to CourseBot Store*\n\n"
        "Your one-stop shop for premium digital courses.\n"
        "Browse, buy, and get instant access to your courses!\n\n"
        "What would you like to do?"
    )
    await query.edit_message_text(
        welcome, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ── CALLBACK ROUTER ───────────────────────────────────────────────────────────
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data  = query.data

    if data == "view_courses":
        await view_courses(update, context)
    elif data == "my_orders":
        await my_orders(update, context)
    elif data in ("view_cart", "cart"):
        await show_cart(update, context)
    elif data.startswith("course_"):
        await show_course_details(update, context)
    elif data.startswith("add_to_cart_"):
        await add_to_cart(update, context)
    elif data.startswith("remove_from_cart_"):
        await remove_from_cart(update, context)
    elif data == "checkout":
        await checkout(update, context)
    elif data == "paid":
        await ask_for_payment_proof(update, context)
    elif data == "back_home":
        await back_to_home(update, context)
    else:
        await query.answer("Unknown action", show_alert=True)


# ── TEXT FALLBACK ─────────────────────────────────────────────────────────────
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "I didn't understand that.\n\nSend */start* to open the store!",
        parse_mode="Markdown",
    )


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main() -> None:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN not found in environment variables!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_proof))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("► E-Commerce Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()