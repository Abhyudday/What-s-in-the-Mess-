
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, time
import pytz

BOT_TOKEN = "7265497857:AAFAfZEgGwMlA3GTR3xQv7G-ah0-hoA8jVQ"

# Mess timetable
meal_schedule = {
    "Breakfast": (time(7, 30), time(8, 30)),
    "Lunch": (time(12, 20), time(14, 0)),
    "Snacks": (time(17, 0), time(18, 0)),
    "Dinner": (time(19, 30), time(21, 0))
}

# Nutrition info for each meal (approx. values)
nutritional_data = {
    "monday": {
        "Breakfast": {"calories": 400, "protein": 10, "carbs": 55, "fat": 12},
        "Lunch": {"calories": 780, "protein": 24, "carbs": 100, "fat": 26},
        "Snacks": {"calories": 480, "protein": 9, "carbs": 60, "fat": 20},
        "Dinner": {"calories": 720, "protein": 20, "carbs": 90, "fat": 24}
    },
    "tuesday": {
        "Breakfast": {"calories": 420, "protein": 9, "carbs": 58, "fat": 13},
        "Lunch": {"calories": 750, "protein": 20, "carbs": 95, "fat": 25},
        "Snacks": {"calories": 460, "protein": 8, "carbs": 62, "fat": 18},
        "Dinner": {"calories": 710, "protein": 21, "carbs": 88, "fat": 22}
    },
    "wednesday": {
        "Breakfast": {"calories": 410, "protein": 10, "carbs": 52, "fat": 11},
        "Lunch": {"calories": 765, "protein": 22, "carbs": 98, "fat": 25},
        "Snacks": {"calories": 450, "protein": 7, "carbs": 55, "fat": 17},
        "Dinner": {"calories": 730, "protein": 23, "carbs": 93, "fat": 23}
    },
    "thursday": {
        "Breakfast": {"calories": 430, "protein": 11, "carbs": 56, "fat": 14},
        "Lunch": {"calories": 745, "protein": 19, "carbs": 92, "fat": 24},
        "Snacks": {"calories": 470, "protein": 8, "carbs": 58, "fat": 19},
        "Dinner": {"calories": 700, "protein": 22, "carbs": 89, "fat": 21}
    },
    "friday": {
        "Breakfast": {"calories": 440, "protein": 10, "carbs": 57, "fat": 15},
        "Lunch": {"calories": 770, "protein": 23, "carbs": 99, "fat": 26},
        "Snacks": {"calories": 460, "protein": 9, "carbs": 60, "fat": 18},
        "Dinner": {"calories": 720, "protein": 21, "carbs": 91, "fat": 22}
    },
    "saturday": {
        "Breakfast": {"calories": 450, "protein": 11, "carbs": 60, "fat": 16},
        "Lunch": {"calories": 740, "protein": 18, "carbs": 90, "fat": 23},
        "Snacks": {"calories": 440, "protein": 7, "carbs": 52, "fat": 17},
        "Dinner": {"calories": 710, "protein": 20, "carbs": 87, "fat": 21}
    },
    "sunday": {
        "Breakfast": {"calories": 430, "protein": 10, "carbs": 54, "fat": 13},
        "Lunch": {"calories": 760, "protein": 22, "carbs": 94, "fat": 25},
        "Snacks": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
        "Dinner": {"calories": 700, "protein": 19, "carbs": 86, "fat": 20}
    }
}

# Mess menu
menu = {
    # same as provided in your code...
    # skipped here for brevity, assumed already defined
}

def get_today_menu(meal_type):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A").lower()
    items = menu.get(today, {}).get(meal_type, "No data for this meal.")
    nutrition = nutritional_data.get(today, {}).get(meal_type, None)
    nutrition_text = ""
    if nutrition:
        nutrition_text = (
            f"\\n\\n⚖️ *Approximate Health Info* (2 rotis or 1 cup rice equivalent):\\n"
            f"🔸 *Calories*: {nutrition['calories']} kcal\\n"
            f"🔸 *Protein*: {nutrition['protein']} g\\n"
            f"🔸 *Carbs*: {nutrition['carbs']} g\\n"
            f"🔸 *Fat*: {nutrition['fat']} g"
        )
    return items + nutrition_text

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
        "👋 Welcome to the Mess Bot!\\nClick below to check what’s in the mess now:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 What’s in Mess", callback_data="next_meal")]])
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "next_meal":
        next_meal = get_next_meal()
        menu_text = get_today_menu(next_meal)
        await query.edit_message_text(
            f"🍽️ *Today's {next_meal} Menu:*\\n\\n{menu_text}",
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )
    elif query.data in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
        meal = query.data
        menu_text = get_today_menu(meal)
        await query.edit_message_text(
            f"📅 *Today's {meal} Menu:*\\n\\n{menu_text}",
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🍽️ Mess Bot is live!")
    app.run_polling()
