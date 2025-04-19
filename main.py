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

# Mess menu from image
menu = {
    "monday": {
        "Breakfast": "Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits",
        "Lunch": "Mix Veg with Paneer + Rajma + Roti + Rice + Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "Aaloo Tikki/Papdi Chat (5 pc) + Matar + Curd + Sonth + Hari Chutney + Chaat Masala + Tea",
        "Dinner": "Arhar Dal + Aloo Palak + Rice + Suji Halwa / Kheer (+Matar Mushroom once/month) + Moong Dal Halwa (once/month) + Onion Salad"
    },
    "tuesday": {
        "Breakfast": "Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits",
        "Lunch": "Tahari + Aloo Tamatar Sabji + Roti + Salad + Curd + Lemon 1/2 + Hari Chutney",
        "Snacks": "Chowmein / Pasta + Tomato Sauce + Chili Sauce + Coffee",
        "Dinner": "Kali Massor Dal + Aloo Beans + Rice + Roti + Ice Cream (Strawberry/Butterscotch/Chocolate/Mango) + Onion Salad"
    },
    "wednesday": {
        "Breakfast": "Plain Paratha + Aloo Tamater Sabji + Pickle + Tea + Milk + Seasonal Fruits",
        "Lunch": "Kaabli Chole (small) + Kashifal + Roti + Jeera Rice + Mix Salad + Curd + Lemon 1/2",
        "Snacks": "Samosa + Chili Sauce + Sonth + Tea",
        "Dinner": "(Mattar/Kadahi) Paneer + Aloo Began Tomato Chokha + Puri + Pulaw + Onion Salad"
    },
    "thursday": {
        "Breakfast": "Pav Bhaji + Tea + Milk + Butter + Seasonal Fruits",
        "Lunch": "Aloo Pyaaj + Kadhi + Rice + Roti + Salad + Fried Papad + Lemon 1/2",
        "Snacks": "Bread Pakoda / Rusk (6 pcs) + Sonath + Hari Chutney + Tea",
        "Dinner": "Aloo Gobhi Mattar with Gravy + Chana Dal + Roti + Rice + Gulab Jamun + Onion Salad"
    },
    "friday": {
        "Breakfast": "Aloo Pyaj Paratha + Pickle + Curd + Tea + Seasonal Fruits",
        "Lunch": "Aloo Gobhi Mattar + Arhar Dal + Roti + Rice + Mix Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "Patties + Tomato Sauce + Coffee",
        "Dinner": "Lauki Kofta + Mix Veg + Arhar Dal + Aloo Soyabeen + Onion Rice + Roti + Besan Ladoo + Onion Salad"
    },
    "saturday": {
        "Breakfast": "Aloo Tamatar Sabji + Ajwain Poori + Fry Mirchi + Tea + Jalebi + Curd + Seasonal Fruits",
        "Lunch": "Louki Fry + Arhar Dal + Roti + Rice + Salad + Curd + Lemon 1/2",
        "Snacks": "Namkeen Jave / Poha + Chili Sauce + Tomato Sauce + Coffee",
        "Dinner": "Rajma + Aloo Bhujia + Jeera Rice + Roti + Onion Salad"
    },
    "sunday": {
        "Breakfast": "Rosted Bread + Aloo Sandwich + Tomato Sauce + Cornflakes + Milk + Tea + Seasonal Fruits",
        "Lunch": "Chole (Kabuli Chane Big) + Bhature + Fried Mirch + Sirka Pyaaz + Jeera Rice + Cold Drink + Pickle + Veg Raita",
        "Snacks": "OFF",
        "Dinner": "Mix Dal + Aloo Kala Chana + Roti + Rice + Sewai + Onion Salad"
    },
}

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
        "👋 Welcome to the Mess Bot!\nClick below to check what’s in the mess now:",
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

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🍽️ Mess Bot is live!")
    app.run_polling()
