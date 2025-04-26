from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, time
import pytz
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
BOT_TOKEN = "7265497857:AAFAfZEgGwMlA3GTR3xQv7G-ah0-hoA8jVQ"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage
user_data = {}
user_count = 0

# Updated Mess Menu (No protein info)
menu = {
    "Monday": {
        "Breakfast": "Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits",
        "Lunch": "Mix Veg with Paneer + Rajma + Roti + Rice + Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "Aaloo Tikki / Papdi Chat (5 piece) + Matar + Curd + Sonth + Hari Chutney + Chaat Masala + Roohafza",
        "Dinner": "Arahar Daal + Bhindi + Rice + Roti + Suji Halwa (Matar Mushroom once in a month / Moong Daal Halwa once in a month) + Onion Salad"
    },
    "Tuesday": {
        "Breakfast": "Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits",
        "Lunch": "Tahari + Aloo Tamatar Sabji + Roti + Salad + Curd + Lemon 1/2 + Hari Chutney",
        "Snacks": "Chowmein / Pasta + Tomato Sauce + Chili Sauce + Shikanji",
        "Dinner": "Kali Massor Daal + Kathal + Rice + Roti + Ice Cream (Mango / Butterscotch / Vanilla) + Onion Salad"
    },
    "Wednesday": {
        "Breakfast": "Aloo Paratha + Pickle + Curd + Milk + Tea + Seasonal Fruits",
        "Lunch": "Kaabli Chhole (Small) + Kashifal + Roti + Jeera Rice + Mix Salad + Curd + Lemon 1/2",
        "Snacks": "Samosa + Chili Sauce + Sonath + Tea",
        "Dinner": "(Matar/Kadahi) Paneer + Aloo Began Tomato Chokha + Puri + Pulav + Onion Salad"
    },
    "Thursday": {
        "Breakfast": "Pav Bhaji + Tea + Milk + Butter + Seasonal Fruits",
        "Lunch": "Aloo Pyaaj + Kadhi + Rice + Roti + Salad + Fried Papad + Lemon 1/2",
        "Snacks": "Bread Pakoda / Rusk (5 pcs) + Sonath + Hari Chatney + Tea",
        "Dinner": "Chana Dal + Aloo Parval + Roti + Rice + Gulab Jamun + Masala Chaach"
    },
    "Friday": {
        "Breakfast": "Aaloo Pyaaj Paratha + Pickle + Curd + Tea + Seasonal Fruits",
        "Lunch": "Aaloo Gobhi Mattar + Arhar Daal + Roti + Rice + Mix Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "Patties + Tomato Sauce + Tea",
        "Dinner": "Arhar Dal + Aaloo Soyabean / Karela + Rice + Roti + Besan Ladoo + Masala Chaach"
    },
    "Saturday": {
        "Breakfast": "Aaloo Tamatar Sabji + Ajwain Poori + Fry Mirchi + Tea + Jalebi + Curd + Seasonal Fruits",
        "Lunch": "Louki Dry + Arhar Dal + Roti + Rice + Salad + Curd + Lemon 1/2",
        "Snacks": "Poha + Chili Sauce + Tomato Sauce + Chat Masala + Shikanji",
        "Dinner": "Rajma + Aaloo Bhujia + Jeera Rice + Roti + Masala Chaach"
    },
    "Sunday": {
        "Breakfast": "Rosted Bread + Aloo Sandwich + Tomato Sauce + Cornflakes Milk + Tea + Seasonal Fruits",
        "Lunch": "Chole (Kabuli Chane Big) + Bhature + Fried Mirch + Sirka Pyaaj + Jeera Rice + Cold Drink + Pickle + Veg Raita",
        "Snacks": "OFF",
        "Dinner": "Mix Dal + Aaloo Kala Chana / Arbi + Roti + Rice + Kheer / Sewai + Onion Salad"
    }
}

meal_times = {
    "Breakfast": (7, 9),
    "Lunch": (12, 14),
    "Snacks": (16, 17),
    "Dinner": (19, 21),
}

def get_current_meal():
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    for meal, (start_hour, end_hour) in meal_times.items():
        if (current_hour == start_hour and current_minute >= 0) or (start_hour < current_hour < end_hour) or (current_hour == end_hour and current_minute == 0):
            return meal
    # If no meal ongoing, return next meal
    if current_hour < 7:
        return "Breakfast"
    elif current_hour < 12:
        return "Lunch"
    elif current_hour < 16:
        return "Snacks"
    elif current_hour < 19:
        return "Dinner"
    else:
        return "Breakfast"  # After dinner, next is breakfast

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_count
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = True
        user_count += 1

    keyboard = [
        [InlineKeyboardButton("What's in Mess?", callback_data='mess')],
        [InlineKeyboardButton(f"Total Users: {user_count}", callback_data='users')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to the Mess Menu Bot!', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_count
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = True
        user_count += 1

    if query.data == 'mess':
        day = datetime.now().strftime("%A")
        meal = get_current_meal()
        today_menu = menu.get(day, {})
        meal_info = today_menu.get(meal, "No info available.")
        await query.edit_message_text(text=f"Today is {day}.\nCurrent Meal: {meal}\n\nMenu:\n{meal_info}")
    elif query.data == 'users':
        await query.edit_message_text(text=f"Total Unique Users: {user_count}")

def main() -> None:
    application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()

    app.add_handler(CommandHandler("user_count", user_count))

    print("🍽️ Mess Bot is live!")
    app.run_polling()
