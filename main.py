from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, time
import pytz

BOT_TOKEN = "7265497857:AAFAfZEgGwMlA3GTR3xQv7G-ah0-hoA8jVQ"
user_ids = set()

# Mess timetable
meal_schedule = {
    "Breakfast": (time(7, 30), time(8, 30)),
    "Lunch": (time(12, 20), time(14, 0)),
    "Snacks": (time(17, 0), time(18, 0)),
    "Dinner": (time(19, 30), time(21, 0))
}

# Mess menu
menu = {
    "Monday": {
        "Breakfast": "🍽️ Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits",
        "Lunch": "🍛 Mix Veg with Paneer + Rajma + Roti + Rice + Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "🍟 Aaloo Tikki / Papdi Chat + Matar + Curd + Sonth + Hari Chutney + Roohafza",
        "Dinner": "🍚 Arahar Daal + Bhindi + Rice + Roti + Suji Halwa + Onion Salad"
    },
    "Tuesday": {
        "Breakfast": "🍽️ Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits",
        "Lunch": "🍛 Tahari + Aloo Tamatar Sabji + Roti + Salad + Curd + Lemon 1/2",
        "Snacks": "🍝 Chowmein / Pasta + Tomato Sauce + Chili Sauce + Shikanji",
        "Dinner": "🍚 Kali Massor Daal + Kathal + Rice + Roti + Ice Cream + Onion Salad"
    },
    "Wednesday": {
        "Breakfast": "🍽️ Aloo Paratha + Pickle + Curd + Milk + Tea + Seasonal Fruits",
        "Lunch": "🍛 Kaabli Chhole + Kashifal + Roti + Jeera Rice + Mix Salad + Curd + Lemon 1/2",
        "Snacks": "🥟 Samosa + Chili Sauce + Sonath + Tea",
        "Dinner": "🍚 (Matar/Kadahi) Paneer + Aloo Began Tomato Chokha + Puri + Pulav + Onion Salad"
    },
    "Thursday": {
        "Breakfast": "🍽️ Pav Bhaji + Tea + Milk + Butter + Seasonal Fruits",
        "Lunch": "🍛 Aloo Pyaaj + Kadhi + Rice + Roti + Salad + Fried Papad + Lemon 1/2",
        "Snacks": "🍞 Bread Pakoda / Rusk + Sonath + Hari Chatney + Tea",
        "Dinner": "🍚 Chana Dal + Aloo Parval + Roti + Rice + Gulab Jamun + Masala Chaach"
    },
    "Friday": {
        "Breakfast": "🍽️ Aaloo Pyaaj Paratha + Pickle + Curd + Tea + Seasonal Fruits",
        "Lunch": "🍛 Aaloo Gobhi Mattar + Arhar Daal + Roti + Rice + Mix Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "🥐 Patties + Tomato Sauce + Tea",
        "Dinner": "🍚 Arhar Dal + Aaloo Soyabean / Karela + Rice + Roti + Besan Ladoo + Masala Chaach"
    },
    "Saturday": {
        "Breakfast": "🍽️ Aaloo Tamatar Sabji + Ajwain Poori + Fry Mirchi + Tea + Jalebi + Curd + Seasonal Fruits",
        "Lunch": "🍛 Louki Dry + Arhar Dal + Roti + Rice + Salad + Curd + Lemon 1/2",
        "Snacks": "🍛 Poha + Chili Sauce + Tomato Sauce + Chat Masala + Shikanji",
        "Dinner": "🍚 Rajma + Aaloo Bhujia + Jeera Rice + Roti + Masala Chaach"
    },
    "Sunday": {
        "Breakfast": "🍽️ Roasted Bread + Aloo Sandwich + Tomato Sauce + Cornflakes Milk + Tea + Seasonal Fruits",
        "Lunch": "🍛 Chole + Bhature + Fried Mirch + Sirka Pyaaj + Jeera Rice + Cold Drink + Pickle + Veg Raita",
        "Snacks": "🚫 OFF",
        "Dinner": "🍚 Mix Dal + Aaloo Kala Chana / Arbi + Roti + Rice + Kheer / Sewai + Onion Salad"
    }
}

def get_today_menu(meal_type):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A")
    today_menu = menu.get(today, {})
    menu_item = today_menu.get(meal_type, "No data for this meal.")
    return today, menu_item

def get_current_or_next_meal():
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    for meal, (start, end) in meal_schedule.items():
        if start <= now <= end:
            return meal  # Current ongoing meal
    for meal, (start, _) in meal_schedule.items():
        if now < start:
            return meal
    return "Breakfast"  # After Dinner, show Breakfast for next day

def build_meal_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥣 Breakfast", callback_data="Breakfast")],
        [InlineKeyboardButton("🍛 Lunch", callback_data="Lunch")],
        [InlineKeyboardButton("🍪 Snacks", callback_data="Snacks")],
        [InlineKeyboardButton("🍽️ Dinner", callback_data="Dinner")],
        [InlineKeyboardButton("📅 Choose a Day", callback_data="choose_day")],
    ])

def build_day_buttons():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    buttons = [[InlineKeyboardButton(day, callback_data=day)] for day in days]
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)

    await update.message.reply_text(
        "👋 Welcome to the Mess Bot!\nClick below to check what’s in the mess now:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 What’s in Mess", callback_data="next_meal")]])
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "next_meal":
        current_or_next_meal = get_current_or_next_meal()
        day, menu_text = get_today_menu(current_or_next_meal)
        await query.edit_message_text(
            f"🍽️ *{day}'s {current_or_next_meal} Menu:*\n\n{menu_text}",
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )
    elif query.data in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
        meal = query.data
        day, menu_text = get_today_menu(meal)
        await query.edit_message_text(
            f"📅 *{day}'s {meal} Menu:*\n\n{menu_text}",
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )
    elif query.data == "choose_day":
        await query.edit_message_text(
            "📅 *Choose a Day for Menu:*",
            reply_markup=build_day_buttons()
        )
    elif query.data in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        day = query.data
        meal = get_current_or_next_meal()
        menu_text = menu.get(day, {}).get(meal, "No data for this meal.")
        await query.edit_message_text(
            f"📅 *{day}'s {meal} Menu:*\n\n{menu_text}",
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )
    elif query.data == "back_to_main":
        await query.edit_message_text(
            "👋 Welcome to the Mess Bot!\nClick below to check what’s in the mess now:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 What’s in Mess", callback_data="next_meal")]])
        )

async def user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = len(user_ids)
    await update.message.reply_text(f"Total users interacting with the bot: {total_users}")

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("user_count", user_count))

    print("🍽️ Mess Bot is live!")
    app.run_polling()
