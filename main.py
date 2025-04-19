from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, time
import pytz

BOT_TOKEN = "7265497857:AAFAfZEgGwMlA3GTR3xQv7G-ah0-hoA8jVQ"

# Meal timings (IST)
meal_schedule = {
    "Breakfast": (time(7, 30), time(8, 30)),
    "Lunch": (time(12, 20), time(14, 0)),
    "Snacks": (time(17, 0), time(18, 0)),
    "Dinner": (time(19, 30), time(21, 0))
}

# Full menu (you can replace this with your full one as needed)
menu = {
    "monday": {
        "Breakfast": "Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits",
        "Lunch": "Mix Veg with Paneer + Rajma + Roti (3) + Rice + Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "Aaloo Tikki/Papdi Chat (5 pc) + Matar + Curd + Sonth + Hari Chutney + Tea",
        "Dinner": "Arhar Dal + Aloo Palak + Rice + Suji Halwa / Kheer + Onion Salad"
    },
    "tuesday": {
        "Breakfast": "Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits",
        "Lunch": "Tahari + Aloo Tamatar Sabji + Roti (3) + Salad + Curd + Lemon 1/2 + Hari Chutney",
        "Snacks": "Chowmein / Pasta + Tomato Sauce + Chili Sauce + Coffee",
        "Dinner": "Kali Massor Dal + Aloo Beans + Rice + Roti (3) + Ice Cream + Onion Salad"
    },
    # Add remaining days...
}

# Suggestion storage (in memory for now)
suggestions = []

def get_today_menu(meal_type):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A").lower()
    return menu.get(today, {}).get(meal_type, "No data for this meal.")

def get_next_meal():
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    for meal, (start, end) in meal_schedule.items():
        if now < start:
            return meal
    return "Breakfast (next day)"

def build_meal_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥣 Breakfast", callback_data="Breakfast")],
        [InlineKeyboardButton("🍛 Lunch", callback_data="Lunch")],
        [InlineKeyboardButton("🍪 Snacks", callback_data="Snacks")],
        [InlineKeyboardButton("🍽️ Dinner", callback_data="Dinner")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to the Mess Bot!*\n\n"
        "Here’s what you can do:\n"
        "• Tap 📅 What’s in Mess to check the upcoming meal\n"
        "• Use `/menu <day>` to check meals for any day (e.g., `/menu tuesday`)\n"
        "• Use `/suggest` to send your feedback or suggestions\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 What’s in Mess", callback_data="next_meal")]])
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "next_meal":
        next_meal = get_next_meal()
        menu_text = get_today_menu(next_meal)
        await query.edit_message_text(
            f"🍽️ *Today's {next_meal} Menu:*\n\n{menu_text}",
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )
    elif query.data in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
        meal = query.data
        menu_text = get_today_menu(meal)
        await query.edit_message_text(
            f"📅 *Today's {meal} Menu:*\n\n{menu_text}",
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❗Usage: /menu <day>\nExample: `/menu tuesday`", parse_mode="Markdown")
        return

    day = context.args[0].lower()
    if day not in menu:
        await update.message.reply_text("❌ Invalid day! Please try: monday, tuesday, ...")
        return

    meals = menu[day]
    msg = f"📅 *{day.capitalize()} Menu:*\n\n"
    for meal, items in meals.items():
        msg += f"*{meal}:* {items}\n\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# Suggest command
async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Please type your suggestion now. I’ll save it!")

    return 1  # Next state in conversation (expecting message)

# Handle user reply for suggestion
async def receive_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    suggestion_text = update.message.text
    user = update.effective_user.first_name
    suggestions.append((user, suggestion_text))
    await update.message.reply_text("✅ Thanks for your suggestion!")

    return -1  # End of conversation

from telegram.ext import ConversationHandler

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))

    suggestion_conv = ConversationHandler(
        entry_points=[CommandHandler("suggest", suggest)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_suggestion)]},
        fallbacks=[],
    )

    app.add_handler(suggestion_conv)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🍽️ Mess Bot is live!")
    app.run_polling()
