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

# Mess menu with protein content (in grams)
menu = {
    "monday": {
        "Breakfast": {"items": "Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits", "protein": 10},
        "Lunch": {"items": "Mix Veg with Paneer + Rajma + Roti + Rice + Salad + Boondi Raita + Lemon 1/2", "protein": 18},
        "Snacks": {"items": "Aaloo Tikki/Papdi Chat (5 pc) + Matar + Curd + Sonth + Hari Chutney + Chaat Masala + Tea", "protein": 12},
        "Dinner": {"items": "Arhar Dal + Aloo Palak + Rice + Suji Halwa / Kheer (+Matar Mushroom once/month) + Moong Dal Halwa (once/month) + Onion Salad", "protein": 22}
    },
    "tuesday": {
        "Breakfast": {"items": "Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits", "protein": 14},
        "Lunch": {"items": "Tahari + Aloo Tamatar Sabji + Roti + Salad + Curd + Lemon 1/2 + Hari Chutney", "protein": 16},
        "Snacks": {"items": "Chowmein / Pasta + Tomato Sauce + Chili Sauce + Coffee", "protein": 10},
        "Dinner": {"items": "Kali Massor Dal + Aloo Beans + Rice + Roti + Ice Cream (Strawberry/Butterscotch/Chocolate/Mango) + Onion Salad", "protein": 21}
    },
    "wednesday": {
        "Breakfast": {"items": "Plain Paratha + Aloo Tamater Sabji + Pickle + Tea + Milk + Seasonal Fruits", "protein": 12},
        "Lunch": {"items": "Kaabli Chole (small) + Kashifal + Roti + Jeera Rice + Mix Salad + Curd + Lemon 1/2", "protein": 20},
        "Snacks": {"items": "Samosa + Chili Sauce + Sonth + Tea", "protein": 6},
        "Dinner": {"items": "(Mattar/Kadahi) Paneer + Aloo Began Tomato Chokha + Puri + Pulaw + Onion Salad", "protein": 28}
    },
    "thursday": {
        "Breakfast": {"items": "Pav Bhaji + Tea + Milk + Butter + Seasonal Fruits", "protein": 10},
        "Lunch": {"items": "Aloo Pyaaj + Kadhi + Rice + Roti + Salad + Fried Papad + Lemon 1/2", "protein": 15},
        "Snacks": {"items": "Bread Pakoda / Rusk (6 pcs) + Sonath + Hari Chutney + Tea", "protein": 8},
        "Dinner": {"items": "Aloo Gobhi Mattar with Gravy + Chana Dal + Roti + Rice + Gulab Jamun + Onion Salad", "protein": 22}
    },
    "friday": {
        "Breakfast": {"items": "Aloo Pyaj Paratha + Pickle + Curd + Tea + Seasonal Fruits", "protein": 14},
        "Lunch": {"items": "Aloo Gobhi Mattar + Arhar Dal + Roti + Rice + Mix Salad + Boondi Raita + Lemon 1/2", "protein": 20},
        "Snacks": {"items": "Patties + Tomato Sauce + Coffee", "protein": 5},
        "Dinner": {"items": "Lauki Kofta + Mix Veg + Arhar Dal + Aloo Soyabeen + Onion Rice + Roti + Besan Ladoo + Onion Salad", "protein": 25}
    },
    "saturday": {
        "Breakfast": {"items": "Aloo Tamatar Sabji + Ajwain Poori + Fry Mirchi + Tea + Jalebi + Curd + Seasonal Fruits", "protein": 12},
        "Lunch": {"items": "Louki Fry + Arhar Dal + Roti + Rice + Salad + Curd + Lemon 1/2", "protein": 18},
        "Snacks": {"items": "Namkeen Jave / Poha + Chili Sauce + Tomato Sauce + Coffee", "protein": 7},
        "Dinner": {"items": "Rajma + Aloo Bhujia + Jeera Rice + Roti + Onion Salad", "protein": 21}
    },
    "sunday": {
        "Breakfast": {"items": "Rosted Bread + Aloo Sandwich + Tomato Sauce + Cornflakes + Milk + Tea + Seasonal Fruits", "protein": 12},
        "Lunch": {"items": "Chole (Kabuli Chane Big) + Bhature + Fried Mirch + Sirka Pyaaz + Jeera Rice + Cold Drink + Pickle + Veg Raita", "protein": 22},
        "Snacks": {"items": "OFF", "protein": 0},
        "Dinner": {"items": "Mix Dal + Aloo Kala Chana + Roti + Rice + Sewai + Onion Salad", "protein": 20}
    },
}

def get_today_menu(meal_type):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A").lower()
    menu_item = menu.get(today, {}).get(meal_type, {"items": "No data for this meal.", "protein": 0})
    return f"{menu_item['items']}\n\nApproximate Protein: {menu_item['protein']} grams"

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
