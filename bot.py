import os
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
    "1": {
        "name": "► learn figma design in 50 minutes",
        "price": "5000 FCFA",
        "description": "Are you ready to learn how to design in Figma in just 50 minutes?  In this video, I'm going to be taking you through everything you need to know about Figma - including an introduction to the platform and a whole lot more. I'll walk through the essential design tools and features, teaching you how you can use them effectively. Along the way, I'll provide tips and tricks on how to create amazing designs using Figma with minimal effort.",
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
        "description": "Welcome to the ultimate coding journey!  In this video, we delve into the fascinating world of HTML for beginners, offering a comprehensive introduction to the essentials of web development. Whether you're a coding novice or looking to strengthen your skills, join us as we unravel the mysteries of HTML and explore the foundations of CSS.",
        "link": "https://youtu.be/El_XZcT3fAk?si=AgBi6oPU2LInsVq8",
        "payment_link": "https://checkout.fapshi.com/link/13735938",
    },
    "5": {
        "name": "► Roadmap to Learning UI/UX Design in 6 Months ",
        "price": "6000 FCFA",
        "description": "Join us as we guide you through each month of this transformative learning journey. From mastering design principles and tools to conducting user research and analysis, creating wireframes and prototypes, diving into visual design and branding, exploring interaction design and animation, and ultimately building a stellar portfolio, this roadmap covers it all Whether you're a beginner looking to break into the world of UI/UX design or an aspiring designer seeking a structured path to success, this roadmap is your ultimate guide to becoming a proficient UI/UX designer in just 6 months.",
        "link": "https://youtu.be/WTNvRAtyZls?si=DiIBWgS0m_JxQZ2g",
        "payment_link": "https://checkout.fapshi.com/link/47655503",
    },
}


# ── /start — HOME PAGE ────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show home page with main menu"""
    keyboard = [
        [InlineKeyboardButton(" View Courses", callback_data="view_courses")],
        [InlineKeyboardButton(" My Orders", callback_data="my_orders")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome = (
        "► *Welcome to CourseBot Store*\n\n"
        "Your one-stop shop for premium digital courses.\n"
        "Browse, buy, and get instant access to your courses!\n\n"
        "What would you like to do?"
    )
    
    await update.message.reply_text(
        welcome,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── VIEW COURSES LIST ─────────────────────────────────────────────────────────
async def view_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show list of available courses"""
    keyboard = [
        [InlineKeyboardButton(f"{info['name']} • {info['price']}", callback_data=f"course_{course_id}")]
        for course_id, info in COURSES.items()
    ]
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_home")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "* Available Courses*\n\nSelect a course to view details:"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


# ── COURSE DETAILS PAGE ───────────────────────────────────────────────────────
async def show_course_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show course details and buy button"""
    query = update.callback_query
    await query.answer()
    
    course_id = query.data.split("_")[1]
    if course_id not in COURSES:
        await query.edit_message_text("❌ Course not found.")
        return
    
    course = COURSES[course_id]
    
    message = (
        f"*{course['name']}*\n\n"
        f"*Price:* {course['price']}\n\n"
        f"ℹ *Description:*\n{course['description']}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("Add to Cart", callback_data=f"add_to_cart_{course_id}")]
        [InlineKeyboardButton("« Back", callback_data="view_courses")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── ADD TO CART ────────────────────────────────────────────────────────────────
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add course to shopping cart"""
    query = update.callback_query
    await query.answer()
    
    course_id = query.data.split("_")[3]
    if course_id not in COURSES:
        await query.edit_message_text("✗ Course not found.")
        return
    
    # Initialize cart if not exists
    if "cart" not in context.user_data:
        context.user_data["cart"] = []
    
    # Add course to cart (avoid duplicates)
    if course_id not in context.user_data["cart"]:
        context.user_data["cart"].append(course_id)
        await query.answer("✓ Course added to cart!", show_alert=True)
    else:
        await query.answer("This course is already in your cart!", show_alert=True)
    
    # Show cart
    await show_cart(update, context)


# ── SHOW CART ──────────────────────────────────────────────────────────────────
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display shopping cart with courses"""
    query = update.callback_query
    
    if "cart" not in context.user_data or not context.user_data["cart"]:
        message = " *Your Cart is Empty*\n\nBrowse courses and add them to your cart!"
        keyboard = [
            [InlineKeyboardButton(" Continue Shopping", callback_data="view_courses")],
        ]
    else:
        cart_items = context.user_data["cart"]
        total_price = 0
        cart_text = " *Your Shopping Cart*\n\n"
        
        for idx, course_id in enumerate(cart_items, 1):
            if course_id in COURSES:
                course = COURSES[course_id]
                # Extract price number
                price_str = course['price'].split()[0]
                try:
                    price_num = int(price_str)
                    total_price += price_num
                except:
                    price_num = 0
                
                cart_text += f"{idx}. {course['name']}\n   {course['price']}\n\n"
        
        cart_text += f"*Total: {total_price} FCFA*"
        message = cart_text
        
        keyboard = []
        for course_id in cart_items:
            if course_id in COURSES:
                course = COURSES[course_id]
                keyboard.append([InlineKeyboardButton(f"✗ Remove: {course['name']}", callback_data=f"remove_from_cart_{course_id}")])
        
        keyboard.append([InlineKeyboardButton("Proceed to Checkout", callback_data="checkout")])
        keyboard.append([InlineKeyboardButton("+ Add More Courses", callback_data="view_courses")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )


# ── REMOVE FROM CART ───────────────────────────────────────────────────────────
async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove course from shopping cart"""
    query = update.callback_query
    await query.answer()
    
    course_id = query.data.split("_")[3]
    
    if "cart" in context.user_data and course_id in context.user_data["cart"]:
        context.user_data["cart"].remove(course_id)
        await query.answer("✓ Course removed from cart!", show_alert=True)
    
    # Refresh cart view
    await show_cart(update, context)


# ── CHECKOUT PAGE ──────────────────────────────────────────────────────────────
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show checkout page with payment instructions"""
    query = update.callback_query
    await query.answer()
    
    if "cart" not in context.user_data or not context.user_data["cart"]:
        await query.edit_message_text("Your cart is empty!")
        return
    
    cart_items = context.user_data["cart"]
    total_price = 0
    course_list = ""
    payment_links = ""
    
    for idx, course_id in enumerate(cart_items, 1):
        if course_id in COURSES:
            course = COURSES[course_id]
            price_str = course['price'].split()[0]
            try:
                price_num = int(price_str)
                total_price += price_num
            except:
                pass
            course_list += f"{idx}. {course['name']} - {course['price']}\n"
            payment_links += f"[Pay for {course['name']}]({course.get('payment_link', 'https://payment.example.com')})\n"
    
    message = (
        f"*Payment Summary*\n\n"
        f"*Courses:*\n{course_list}\n"
        f"*Total: {total_price} FCFA*\n\n"
        f"*Payment Links:*\n{payment_links}\n"
        f"*Steps:*\n"
        f"1. Click the payment link above for each course\n"
        f"2. Complete the payment\n"
        f"3. Take a screenshot of your payment confirmation\n"
        f"4. Upload the screenshot here\n\n"
        f"Once we verify your payment, you'll get instant access to all courses! ✓"
    )
    
    keyboard = [
        [InlineKeyboardButton("✓ I Have Paid", callback_data="paid")],
        [InlineKeyboardButton("« Back to Cart", callback_data="view_cart")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
async def show_payment_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show payment instructions"""
    query = update.callback_query
    await query.answer()
    
    course_id = query.data.split("_")[1]
    if course_id not in COURSES:
        await query.edit_message_text("❌ Course not found.")
        return
    
    course = COURSES[course_id]
    
    # Store selected course
    context.user_data["selected_course"] = course_id
    
    message = (
        f"*Payment for {course['name']}*\n\n"
        f"*Price: {course['price']}*\n\n"
        f"*Payment Methods:*\n"
        f"☎ MTN Mobile Money\n"
        f"☎ Orange Money\n\n"
        f"*Steps:*\n"
        f"1. Send {course['price']} to the provided account\n"
        f"2. Take a screenshot of your payment\n"
        f"3. Upload the screenshot here\n\n"
        f"Once we verify your payment, you'll get instant access! ✓"
    )
    
    keyboard = [
        [InlineKeyboardButton("✓ I Have Paid", callback_data="paid")],
        [InlineKeyboardButton("« Back", callback_data=f"course_{course_id}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── PAYMENT PROOF REQUEST ─────────────────────────────────────────────────────
async def ask_for_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask user to upload payment screenshot"""
    query = update.callback_query
    await query.answer()
    
    message = "*↑ Please upload your payment screenshot*\n\nSend a photo of your payment confirmation."
    
    keyboard = [[InlineKeyboardButton("« Back", callback_data="view_cart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── AUTO DELIVERY ON PHOTO UPLOAD ────────────────────────────────────────────
async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Auto-deliver courses when user sends payment proof photo"""
    cart_items = context.user_data.get("cart", [])
    
    if not cart_items:
        await update.message.reply_text(
            "✗ *Please add courses to cart first*\n\n"
            "Use /start to browse courses.",
            parse_mode="Markdown",
        )
        return
    
    # Build delivery message with all courses
    delivery_message = (
        f"✓ *Payment Received!*\n\n"
        f"► *Here are your courses:*\n\n"
    )
    
    for course_id in cart_items:
        if course_id in COURSES:
            course = COURSES[course_id]
            delivery_message += f"*{course['name']}*\n~ {course['link']}\n\n"
    
    delivery_message += f"Thank you for your purchase! Enjoy your courses! ►"
    
    await update.message.reply_text(
        delivery_message,
        parse_mode="Markdown",
    )
    
    # Clear the cart
    context.user_data.pop("cart", None)


# ── MY ORDERS (Placeholder) ───────────────────────────────────────────────────
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's order history"""
    query = update.callback_query
    await query.answer()
    
    message = " *My Orders*\n\nYou haven't purchased any courses yet.\n\nBrowse our courses to get started!"
    
    keyboard = [
        [InlineKeyboardButton(" View Courses", callback_data="view_courses")],
        [InlineKeyboardButton("« Back", callback_data="back_home")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


# ── BACK BUTTON HANDLERS ──────────────────────────────────────────────────────
async def back_to_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Go back to home page"""
    query = update.callback_query
    await query.answer()
    await start(update, context)


async def back_to_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Go back from payment confirmation"""
    query = update.callback_query
    await query.answer()
    await ask_for_payment_proof(update, context)


# ── CALLBACK QUERY ROUTER ─────────────────────────────────────────────────────
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all callback queries"""
    query = update.callback_query
    callback_data = query.data
    
    if callback_data == "view_courses":
        await view_courses(update, context)
    elif callback_data == "my_orders":
        await my_orders(update, context)
    elif callback_data == "view_cart":
        await show_cart(update, context)
    elif callback_data.startswith("course_"):
        await show_course_details(update, context)
    elif callback_data.startswith("add_to_cart_"):
        await add_to_cart(update, context)
    elif callback_data.startswith("remove_from_cart_"):
        await remove_from_cart(update, context)
    elif callback_data == "checkout":
        await checkout(update, context)
    elif callback_data == "paid":
        await ask_for_payment_proof(update, context)
    elif callback_data == "paid_back":
        await show_cart(update, context)
    elif callback_data == "back_home":
        await back_to_home(update, context)
    else:
        await query.answer("Unknown action", show_alert=True)


# ── HANDLE ANY TEXT MESSAGE ────────────────────────────────────────────────────
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle any random text input and guide user to /start"""
    message = (
        "I didn't understand that command.\n\n"
        "To get started, please send:\n\n"
        "*/start*\n\n"
        "This will show you the home page where you can browse courses!"
    )
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown",
    )


# ── MAIN APPLICATION ─────────────────────────────────────────────────────────
def main() -> None:
    """Initialize and run the bot"""
    # Get token from environment
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN not found in environment variables!")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Callback query handler (inline buttons)
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_proof))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    print("► E-Commerce Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()