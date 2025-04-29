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
"Breakfast": "VEG FRIED IDLI+PLAIN IDLI+SAMBHAR+COCONUT CHATNEY+TEA+MILK+SEASONAL FRUITS",
"Lunch": "MIX VEG WITH PANEER+RAJMA+ROTI+RICE+SALAD+BOONDI RAITA+LEMON1/2",
"Snacks": "ALOO TIKKI/PAPDI CHAT(5 PIECE)+MATAR+CURD+SONTH+HARI CHATNI+CHAAT MASALA+ROOHAFZA",
"Dinner": "ARHAR DAAL+BHINDI +RICE+ROTI+SUJI HALWA+{MATAR MUSHROOM (ONCE IN A MONTH)+MOONG DAAL HALWA(ONCE IN A MONTH)}+ONION SALAD"
},
"Tuesday": {
"Breakfast": "MATAR KULCHE+PICKLE+TEA+MILK+SEASONAL FRUITS",
"Lunch": "TAHARI+ALOO TAMATAR SABJI+ROTI+SALAD+CURD+LEMON 1/2+HARI CHUTNEY",
"Snacks": "CHOWMEIN/PASTA+TOMATO SAUCE+CHILLI+SAUCE+SHIKANJI",
"Dinner": "KALI MASSOR DAL+KATHAL+RICE+ROTI+ICECREAM(MANGO/BUTTERSCOTCH/VANILA)+ONION SALAD"
},
"Wednesday": {
"Breakfast": "ALOO PARATHA+PICKLE+CURD+MILK+TEA+SEASONAL FRUITS",
"Lunch": "KAABLI CHHOLE(SMALL)+KASHIFAL+ROTI+JEERA RICE+MIX SALAD+CURD+LEMON 1/2",
"Snacks": "SAMOSA+CHILI SAUSE+SONATH+TEA",
"Dinner": "(MATTAR/KADHI)+PANEER+ALOO BEGAN TOMATO CHOKHA+PURI+PULAW+ONION SALAD"
},
"Thursday": {
"Breakfast": "PAV BHAJI+TEA+MILK+BUTTER+SEASONAL FRUITS",
"Lunch": "ALOO PYAJA+KADHI+RICE+ROTI+SALAD+FRIED PAPAD+LEMON1/2",
"Snacks": "BREAD PAKODA/RUSK(5PCS)+SONATH+HARI CHATNEY+TEA",
"Dinner": "CHANA DAL+ALOO PARVAL+ROTI+RICE+GULAB JAAMUN+MASALA CHAACH"
},
"Friday": {
"Breakfast": "ALOO PYAJ PARATHA+PICKLE+CURD+TEA+SEASONAL FRUITS",
"Lunch": "AALOO GOBHI MATTAR+ARHAR DAAL+ROTI+RICE+MIX SALAD+BOONDI RAITA+LEMON1/2",
"Snacks": "PATTIES+TOMATO SAUCE+TEA",
"Dinner": "ARHAR DAL+ALOO SOYABEEN/KARELA+RICE+ROTI+BESAN LADOO+MASALA CHAACH"
},
"Saturday": {
"Breakfast": "AALOO TAMATAR SABJI+AJWAIN POORI+FRY MIRCHI+TEA+JALEBI+CURD+SEASONAL FRUITS",
"Lunch": "LOUKI DRY+ARHAR DAL+ROTI+RICE+SALAD+CURD+LEMON 1/2",
"Snacks": "POHA+CHILI SAUCE+TOMATO SAUCE+CHAT MASALA+SHIKANJI",
"Dinner": "RAJMA+ALOO BHUJIYA+JEERA RICE+ROTI+MASALA CHAACH"
},
"Sunday": {
"Breakfast": "ROSTED BREAD+ALOO SANDWICH+TOMATO+SAUCE+CORNFLAKES MILK+TEA+SEASONAL FRUITS",
"Lunch": "CHOLE(KABULI CHANE BIG)+BHATURE+FRIED MIRCH+SIRKA PYAJA+JEERA RICE+COLD DRINK+PICKLE+VEG RAITA",
"Snacks": "OFF",
"Dinner": "MIX DAL+ALOO KALA CHANA/ARBI+ROTI+RICE+KHEER/SEWAI+ONION SALAD"
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
