from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, time
import pytz

# Hardcoded Bot Token
BOT_TOKEN = "7265497857:AAFAfZEgGwMlA3GTR3xQv7G-ah0-hoA8jVQ"

# IST timezone
IST = pytz.timezone("Asia/Kolkata")

# Mess meal schedule
MESS_SCHEDULE = [
    ("Breakfast", time(7, 30), time(8, 30)),
    ("Lunch", time(12, 20), time(14, 0)),
    ("Snacks", time(17, 0), time(18, 0)),
    ("Dinner", time(19, 30), time(21, 0)),
]

# Weekly menu data extracted from image
MESS_MENU = {
    "Monday": {
        "Breakfast": "Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits",
        "Lunch": "Mix Veg with Paneer + Rajma + Roti + Rice + Salad + Boondi Raita + Lemon",
        "Snacks": "Aaloo Tikki / Papdi Chat (5 pcs) + Matar Chutney + Sonth + Hari Chutney + Chaat Masala + Tea",
        "Dinner": "Arhar Dal + Aaloo Palak + Rice + Suji Halwa / Kheer (+Matar Mushroom once/month) + Moong Dal Halwa (once/month) + Onion Salad"
    },
    "Tuesday": {
        "Breakfast": "Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits",
        "Lunch": "Tahari + Aaloo Tamatar Sabji + Roti + Salad + Curd + Lemon + Hari Chutney",
        "Snacks": "Chowmein / Pasta + Tomato Sauce + Chili Sauce + Coffee",
        "Dinner": "Kali Massor Dal + Aaloo Beans + Rice + Roti + Ice Cream (Strawberry/Butterscotch/Chocolate/Mango) + Onion Salad"
    },
    "Wednesday": {
        "Breakfast": "Plain Paratha + Aaloo Tamater Sabji + Pickle + Milk + Tea + Seasonal Fruits",
        "Lunch": "Kaabli Chhole (Small) + Kashifal + Roti + Jeera Rice + Mix Salad + Curd + Lemon",
        "Snacks": "Samosa + Chili Sauce + Sonth + Tea",
        "Dinner": "Matar/Kadahi Paneer + Aaloo Began Tamatar Chokha + Puri + Pulav + Onion Salad"
    },
    "Thursday": {
        "Breakfast": "Pav Bhaji + Tea + Milk + Butter + Seasonal Fruits",
        "Lunch": "Aaloo Pyaaj + Kadhi + Rice + Roti + Salad + Fried Papad + Lemon",
        "Snacks": "Bread Pakoda / Rusk (6 pcs) + Sonth + Hari Chutney + Tea",
        "Dinner": "Aaloo Gobhi Mattar with Gravy + Chana Dal + Roti + Rice + Gulab Jamun + Onion Salad"
    },
    "Friday": {
        "Breakfast": "Aaloo Pyaj Paratha + Pickle + Curd + Tea + Seasonal Fruits",
        "Lunch": "Aaloo Gobhi Mattar + Arhar Dal + Roti + Rice + Mix Salad + Boondi Raita + Lemon",
        "Snacks": "Patties + Tomato Sauce + Coffee",
        "Dinner": "Lauki Kofta + Mix Veg / Arhar Dal + Aaloo Soyabeen + Onion Rice + Roti + Besan Ladoo + Onion Salad"
    },
    "Saturday": {
        "Breakfast": "Aaloo Tamatar Sabji + Ajwain Poori + Fry Mirchi + Tea + Jalebi + Curd + Seasonal Fruits",
        "Lunch": "Louki Fry + Arhar Dal + Roti + Rice + Salad + Curd + Lemon",
        "Snacks": "Namkeen Jave / Poha + Chili Sauce + Tomato Sauce + Coffee",
        "Dinner": "Rajma + Aaloo Bhujia + Jeera Rice + Roti + Onion Salad"
    },
    "Sunday": {
        "Breakfast": "Rosted Bread + Aaloo Sandwich + Tomato Sauce + Cornflakes + Milk + Tea + Seasonal Fruits",
        "Lunch": "Chole (Kabuli Chane Big) + Bhature + Fried Mirch + Sirka Pyaaj + Jeera Rice + Cold Drink + Pickle + Veg Raita",
        "Snacks": "OFF",
        "Dinner": "Mix Dal + Aaloo Kala Chana + Roti + Rice + Sewai + Onion Salad"
    }
}

# Determine current or next meal and get dish
def get_mess_update():
    now = datetime.now(IST)
    today = now.strftime("%A")
    current_time = now.time()

    for meal, start, end in MESS_SCHEDULE:
        if start <= current_time <= end:
            return f"🟢 *{meal}* is currently being served:\n\n🍽️ {MESS_MENU[today][meal]}"
    for meal, start, _ in MESS_SCHEDULE:
        if current_time < start:
            return f"⏭️ Next up is *{meal}*:\n\n🍽️ {MESS_MENU[today][meal]}"
    return "✅ All meals are done for today. Come back tomorrow!"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🍽️ What's in the mess?", callback_data='whats_in_mess')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to the Mess Bot!\nClick below to see what's being served 👇", reply_markup=reply_markup)

# Handle button press
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'whats_in_mess':
        message = get_mess_update()
        await query.edit_message_text(text=message, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🍽️ Mess Bot is live!")
    app.run_polling()

if __name__ == '__main__':
    main()
