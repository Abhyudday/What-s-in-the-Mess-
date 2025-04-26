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

menu = {
"Monday": {
"Breakfast": "🥣 Milk + Cornflakes + Banana / Apple",
"Lunch": "🍛 Rajma + Rice + Roti + Mix Veg + Mix Salad + Lemon 1/2",
"Snacks": "🥪 Veg Sandwich + Green Chutney + Tea",
"Dinner": "🍚 Arahar Daal + Bhindi + Rice + Roti + Suji Halwa + Matar Mushroom (once a month) / Moong Daal Halwa (once a month) + Onion Salad"
},
"Tuesday": {
"Breakfast": "🥣 Milk + Poha + Banana",
"Lunch": "🍛 Kala Chana + Roti + Rice + Lauki + Mix Salad + Lemon 1/2",
"Snacks": "🥔 Aloo Tikki + Hari Chutney + Tea",
"Dinner": "🍚 Kali Massor Daal + Kathal + Rice + Roti + Ice Cream (Mango/Butterscotch/Vanilla) + Onion Salad"
},
"Wednesday": {
"Breakfast": "🥣 Milk + Veg Upma + Apple",
"Lunch": "🍛 Kaabli Chhole (small) + Kashifal + Roti + Jeera Rice + Mix Salad + Curd + Lemon 1/2",
"Snacks": "🍛 Pav Bhaji + Tea",
"Dinner": "🍚 Green Daal + Bhindi + Rice + Roti + Rasgulla + Onion Salad"
},
"Thursday": {
"Breakfast": "🥣 Milk + Suji Dalia + Banana",
"Lunch": "🍛 Green Moong Whole + Rice + Roti + Tinda + Mix Salad + Lemon 1/2",
"Snacks": "🍞 Bread Pakoda / Rusk (5 pcs) + Sonath + Hari Chatney + Tea",
"Dinner": "🍚 Lobiya Whole + Aloo Tamatar + Rice + Roti + Sooji Cake + Onion Salad"
},
"Friday": {
"Breakfast": "🥣 Milk + Aloo Sandwich + Apple",
"Lunch": "🍛 Toor Daal + Roti + Rice + Aloo Gobhi + Mix Salad + Lemon 1/2",
"Snacks": "🥙 Veg Cutlet + Sauce + Tea",
"Dinner": "🍚 Methi Daal + Parwal + Rice + Roti + Fruit Custard + Onion Salad"
},
"Saturday": {
"Breakfast": "🥣 Milk + Besan Chilla + Banana",
"Lunch": "🍛 Urad Daal + Rice + Roti + Kaddu + Mix Salad + Lemon 1/2",
"Snacks": "🥟 Matar Kachori + Aloo Sabji + Tea",
"Dinner": "🍚 Chana Daal + Aloo Tamatar + Rice + Roti + Ice Cream (Mango/Butterscotch/Vanilla) + Onion Salad"
},
"Sunday": {
"Breakfast": "🥣 Milk + Aloo Puri + Raita + Pickle",
"Lunch": "🍛 Chole (Kabuli Chane Big) + Bhature + Fried Mirch + Sirka Pyaaj + Jeera Rice + Cold Drink + Pickle + Veg Raita",
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
