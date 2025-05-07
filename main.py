from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, time, timedelta
import pytz
import os
import sys

BOT_TOKEN = "7265497857:AAFAfZEgGwMlA3GTR3xQv7G-ah0-hoA8jVQ"
user_ids = set()
# Store users who want auto-updates
auto_update_users = set()

# Mess timetable
meal_schedule = {
    "Breakfast": (time(7, 30), time(8, 30)),
    "Lunch": (time(12, 20), time(14, 0)),
    "Snacks": (time(17, 0), time(18, 0)),
    "Dinner": (time(19, 30), time(21, 0))
}
menu = {
    "Monday": {
        "Breakfast": "🍽️ Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits",
        "Lunch": "🍛 Mix Veg with Paneer + Rajma + Roti + Rice + Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "🥔 Aloo Tikki / Papdi Chaat (5 pcs) + Matar + Curd + Sonth + Hari Chutney + Chaat Masala + Roohafza",
        "Dinner": "🍚 Arhar Daal + Bhindi + Rice + Roti + Suji Halwa + (Matar Mushroom (once in a month) / Moong Daal Halwa (once in a month)) + Onion Salad"
    },
    "Tuesday": {
        "Breakfast": "🍽️ Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits",
        "Lunch": "🍛 Tahari + Aloo Tamatar Sabji + Roti + Salad + Curd + Lemon 1/2 + Hari Chutney",
        "Snacks": "🍝 Chowmein / Pasta + Tomato Sauce + Chilli Sauce + Shikanji",
        "Dinner": "🍚 Kali Masoor Daal + Kathal + Rice + Roti + Ice Cream (Mango / Butterscotch / Vanilla) + Onion Salad"
    },
    "Wednesday": {
        "Breakfast": "🍽️ Aloo Paratha + Pickle + Curd + Milk + Tea + Seasonal Fruits",
        "Lunch": "🍛 Kaabli Chhole (Small) + Kashifal + Roti + Jeera Rice + Mix Salad + Curd + Lemon 1/2",
        "Snacks": "🥟 Samosa + Chilli Sauce + Sonth + Tea",
        "Dinner": "🍚 (Mattar / Kadhi) Paneer + Aloo Began Tamatar Chokha + Puri + Pulav + Onion Salad"
    },
    "Thursday": {
        "Breakfast": "🍽️ Pav Bhaji + Tea + Milk + Butter + Seasonal Fruits",
        "Lunch": "🍛 Aloo Pyaaj + Kadhi + Rice + Roti + Salad + Fried Papad + Lemon 1/2",
        "Snacks": "🍞 Bread Pakoda / Rusk (5 pcs) + Sonath + Hari Chatney + Tea",
        "Dinner": "🍚 Chana Daal + Aloo Parval + Roti + Rice + Gulab Jamun + Masala Chaach"
    },
    "Friday": {
        "Breakfast": "🍽️ Aloo Pyaj Paratha + Pickle + Curd + Tea + Seasonal Fruits",
        "Lunch": "🍛 Aloo Gobhi Mattar + Arhar Daal + Roti + Rice + Mix Salad + Boondi Raita + Lemon 1/2",
        "Snacks": "🥙 Patties + Tomato Sauce + Tea",
        "Dinner": "🍚 Arhar Daal + Aloo Soyabeen / Karela + Rice + Roti + Besan Ladoo + Masala Chaach"
    },
    "Saturday": {
        "Breakfast": "🍽️ Aloo Tamatar Sabji + Ajwain Poori + Fry Mirchi + Tea + Jalebi + Curd + Seasonal Fruits",
        "Lunch": "🍛 Louki Dry + Arhar Daal + Roti + Rice + Salad + Curd + Lemon 1/2",
        "Snacks": "🥔 Poha + Chilli Sauce + Tomato Sauce + Chaat Masala + Shikanji",
        "Dinner": "🍚 Rajma + Aloo Bhujia + Jeera Rice + Roti + Masala Chaach"
    },
    "Sunday": {
        "Breakfast": "🍽️ Roasted Bread + Aloo Sandwich + Tomato Sauce + Cornflakes + Milk + Tea + Seasonal Fruits",
        "Lunch": "🍛 Chole (Kabuli Chane Big) + Bhature + Fried Mirch + Sirka Pyaaj + Jeera Rice + Cold Drink + Pickle + Veg Raita",
        "Snacks": "🚫 OFF",
        "Dinner": "🍚 Mix Daal + Aloo / Kala Chana / Arbi + Roti + Rice + Kheer / Sewai + Onion Salad"
    }
}

# Check if bot is already running
def is_bot_running():
    import psutil
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.pid != current_process.pid:  # Skip current process
            try:
                if 'python' in process.name().lower() and 'main.py' in ' '.join(process.cmdline()):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    return False

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
        [InlineKeyboardButton("📅 What's in Mess", callback_data="next_meal")],
        [InlineKeyboardButton("🔔 Toggle Auto Updates", callback_data="toggle_updates")],
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

async def send_meal_notification(context: ContextTypes.DEFAULT_TYPE):
    """Send notifications to users who have opted for auto-updates"""
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    today = now.strftime("%A")
    next_meal = get_current_or_next_meal()
    
    # Get meal time and create timezone-aware datetime
    meal_time = meal_schedule[next_meal][0]
    notification_time = tz.localize(datetime.combine(now.date(), meal_time)) - timedelta(minutes=15)
    
    # Only send if we're within 1 minute of the notification time
    if abs((now - notification_time).total_seconds()) > 60:
        return
    
    message = f"🔔 *Upcoming {next_meal} in 15 minutes!*\n\n🍽️ *{today}'s {next_meal} Menu:*\n\n{menu[today].get(next_meal,'No data')}"
    
    for user_id in auto_update_users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Failed to send notification to {user_id}: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # Handle auto-update toggle
    if data == "toggle_updates":
        user_id = update.effective_user.id
        if user_id in auto_update_users:
            auto_update_users.remove(user_id)
            status = "disabled"
        else:
            auto_update_users.add(user_id)
            status = "enabled"
        
        await query.edit_message_text(
            f"🔔 Auto-updates have been {status}!\nYou will receive notifications 15 minutes before each meal.",
            reply_markup=build_main_buttons()
        )
        return

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
    # Check if bot is already running
    if is_bot_running():
        print("Bot is already running! Exiting...")
        sys.exit(1)
        
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add job to check for notifications every minute
    job_queue = app.job_queue
    job_queue.run_repeating(send_meal_notification, interval=60, first=10)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("user_count", user_count))
    print("Bot started")
    app.run_polling()
