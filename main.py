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


def get_current_or_next_meal():
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    # if within a meal window => that meal
    for meal,(start,end) in meal_schedule.items():
        if start <= now <= end:
            return meal
    # otherwise next upcoming
    for meal,(start,_) in meal_schedule.items():
        if now < start:
            return meal
    return "Breakfast"

def build_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 What’s in Mess", callback_data="next_meal")],
    ])

def build_meal_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥣 Breakfast", callback_data="Breakfast")],
        [InlineKeyboardButton("🍛 Lunch",     callback_data="Lunch")],
        [InlineKeyboardButton("🍪 Snacks",    callback_data="Snacks")],
        [InlineKeyboardButton("🍽️ Dinner",    callback_data="Dinner")],
        [InlineKeyboardButton("📅 Choose a Day", callback_data="choose_day")],
    ])

def build_day_buttons():
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    kb = [[InlineKeyboardButton(d, callback_data=f"day_{d}")] for d in days]
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_ids.add(update.effective_user.id)
    await update.message.reply_text(
        "👋 Welcome to the Mess Bot!",
        reply_markup=build_main_buttons()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # clear selection if we go back
    if data == "back_to_main":
        context.user_data.pop("selected_day", None)
        await query.edit_message_text(
            "👋 Welcome back! What would you like?",
            reply_markup=build_main_buttons()
        )
        return

    # next_meal on main
    if data == "next_meal":
        context.user_data.pop("selected_day", None)
        meal = get_current_or_next_meal()
        today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A")
        text = f"🍽️ *{today}'s {meal} Menu:*\n\n{menu[today].get(meal,'No data')}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_meal_buttons())
        return

    # choose day
    if data == "choose_day":
        await query.edit_message_text("📅 *Choose a day:*", parse_mode="Markdown", reply_markup=build_day_buttons())
        return

    # day selected
    if data.startswith("day_"):
        day = data.split("_",1)[1]
        context.user_data["selected_day"] = day
        # show that day's current/next meal
        meal = get_current_or_next_meal()
        text = f"🍽️ *{day}'s {meal} Menu:*\n\n{menu[day].get(meal,'No data')}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_meal_buttons())
        return

    # meal button (Breakfast/Lunch/Snacks/Dinner)
    if data in meal_schedule:
        # if a day was chosen, use that, otherwise today
        day = context.user_data.get("selected_day") or datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A")
        text = f"🍽️ *{day}'s {data} Menu:*\n\n{menu[day].get(data,'No data')}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_meal_buttons())
        return

async def user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Total users: {len(user_ids)}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("user_count", user_count))
    print("Bot started")
    app.run_polling()
