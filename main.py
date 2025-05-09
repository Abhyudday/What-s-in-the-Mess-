from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from datetime import datetime, time, timedelta
import pytz
import os
import sys
import logging
import redis
import json

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN', "8081749044:AAEyaV3xrW6KFQuIcHIkugJAFzB54NRemNA")
ADMIN_ID = int(os.getenv('ADMIN_ID', "5950741458"))  # Your admin ID as default value
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Initialize Redis
redis_client = redis.from_url(REDIS_URL)

def load_user_data():
    """Load user data from Redis"""
    try:
        # Load user IDs
        user_ids_str = redis_client.get('user_ids')
        user_ids = set(json.loads(user_ids_str)) if user_ids_str else set()
        
        # Load auto update users
        auto_update_str = redis_client.get('auto_update_users')
        auto_update_users = json.loads(auto_update_str) if auto_update_str else {}
        
        return user_ids, auto_update_users
    except Exception as e:
        logger.error(f"Error loading from Redis: {e}")
        return set(), {}

def save_user_data(user_ids, auto_update_users):
    """Save user data to Redis"""
    try:
        # Save user IDs
        redis_client.set('user_ids', json.dumps(list(user_ids)))
        # Save auto update users
        redis_client.set('auto_update_users', json.dumps(auto_update_users))
    except Exception as e:
        logger.error(f"Error saving to Redis: {e}")

# Load initial data
user_ids, auto_update_users = load_user_data()

# States for conversation handler
SETTING_TIME = 1

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
        [InlineKeyboardButton("📅 Today's Menu", callback_data="next_meal")],
        [InlineKeyboardButton("🔔 Enable Auto Updates", callback_data="enable_updates")],
        [InlineKeyboardButton("🔕 Disable Auto Updates", callback_data="disable_updates")],
        [InlineKeyboardButton("⏰ Set Notification Time", callback_data="set_time")],
    ])

def build_meal_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🥣 Breakfast", callback_data="Breakfast"),
            InlineKeyboardButton("🍛 Lunch", callback_data="Lunch")
        ],
        [
            InlineKeyboardButton("🍪 Snacks", callback_data="Snacks"),
            InlineKeyboardButton("🍽️ Dinner", callback_data="Dinner")
        ],
        [InlineKeyboardButton("📅 Choose a Day", callback_data="choose_day")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])

def build_day_buttons():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    kb = []
    # Create rows of 2 buttons each
    for i in range(0, len(days), 2):
        row = []
        row.append(InlineKeyboardButton(days[i], callback_data=f"day_{days[i]}"))
        if i + 1 < len(days):
            row.append(InlineKeyboardButton(days[i + 1], callback_data=f"day_{days[i + 1]}"))
        kb.append(row)
    # Add back button at the bottom
    kb.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")])
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_ids.add(update.effective_user.id)
    save_user_data(user_ids, auto_update_users)  # Save after adding new user
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
    
    for user_id, user_prefs in auto_update_users.items():
        try:
            # Get user's preferred notification time (default to 15 minutes before if not set)
            notification_minutes = user_prefs.get('notification_minutes', 15)
            notification_time = tz.localize(datetime.combine(now.date(), meal_time)) - timedelta(minutes=notification_minutes)
    
    # Only send if we're within 1 minute of the notification time
            if abs((now - notification_time).total_seconds()) <= 60:
                message = f"🔔 *Upcoming {next_meal} in {notification_minutes} minutes!*\n\n🍽️ *{today}'s {next_meal} Menu:*\n\n{menu[today].get(next_meal,'No data')}"
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")

async def set_notification_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle setting custom notification time"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⏰ Please enter how many minutes before the meal you want to be notified (1-60):\n"
        "For example, send '15' to get notified 15 minutes before each meal.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="back_to_main")]])
    )
    return SETTING_TIME

async def handle_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the user's time input"""
    try:
        minutes = int(update.message.text)
        if 1 <= minutes <= 60:
            user_id = update.effective_user.id
            if user_id not in auto_update_users:
                auto_update_users[user_id] = {}
            auto_update_users[user_id]['notification_minutes'] = minutes
            save_user_data(user_ids, auto_update_users)  # Save after updating preferences
            await update.message.reply_text(
                f"✅ You will now be notified {minutes} minutes before each meal!",
                reply_markup=build_main_buttons()
            )
        else:
            await update.message.reply_text(
                "❌ Please enter a number between 1 and 60.",
                reply_markup=build_main_buttons()
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Please enter a valid number.",
            reply_markup=build_main_buttons()
        )
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # Handle auto-update enable
    if data == "enable_updates":
        user_id = update.effective_user.id
        if user_id not in auto_update_users:
            auto_update_users[user_id] = {'notification_minutes': 15}  # Default 15 minutes
            save_user_data(user_ids, auto_update_users)  # Save after enabling updates
        await query.edit_message_text(
            "🔔 Auto-updates have been enabled!\n"
            "You will receive notifications before each meal.\n"
            "Use 'Set Notification Time' to customize when you want to be notified.",
            reply_markup=build_main_buttons()
        )
        return

    # Handle auto-update disable
    if data == "disable_updates":
        user_id = update.effective_user.id
        if user_id in auto_update_users:
            del auto_update_users[user_id]
            save_user_data(user_ids, auto_update_users)  # Save after disabling updates
        await query.edit_message_text(
            "🔕 Auto-updates have been disabled!\n"
            "You will no longer receive meal notifications.",
            reply_markup=build_main_buttons()
        )
        return

    # Handle set time button
    if data == "set_time":
        return await set_notification_time(update, context)

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
    """Show total number of users"""
    total_users = len(user_ids)
    active_updates = len(auto_update_users)
    await update.message.reply_text(
        f"📊 *User Statistics:*\n"
        f"👥 Total Users: {total_users}\n"
        f"🔔 Users with Auto Updates: {active_updates}",
        parse_mode="Markdown"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast a message to all users"""
    # Check if user is authorized
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to broadcast messages.")
        return

    # Get the message to broadcast
    if not context.args:
        await update.message.reply_text("Please provide a message to broadcast.\nUsage: /broadcast <message>")
        return

    message = " ".join(context.args)
    success_count = 0
    fail_count = 0

    # Load fresh user IDs from Redis
    current_user_ids, _ = load_user_data()

    for user_id in current_user_ids:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 *Broadcast Message:*\n\n{message}",
                parse_mode="Markdown"
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
            fail_count += 1

    await update.message.reply_text(
        f"📊 Broadcast Results:\n"
        f"✅ Successfully sent: {success_count}\n"
        f"❌ Failed to send: {fail_count}"
    )

if __name__ == "__main__":
    try:
        # Check if bot is already running
        if is_bot_running():
            print("Bot is already running! Exiting...")
            sys.exit(1)
            
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Add conversation handler for setting notification time
        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(set_notification_time, pattern="^set_time$")],
            states={
                SETTING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time_input)],
            },
            fallbacks=[CallbackQueryHandler(button_handler, pattern="^back_to_main$")]
        )
        
        # Add job to check for notifications every minute
        try:
            job_queue = app.job_queue
            if job_queue is not None:
                job_queue.run_repeating(send_meal_notification, interval=60, first=10)
                logger.info("Job queue started successfully")
            else:
                logger.warning("Job queue is not available. Auto-updates will not work.")
        except Exception as e:
            logger.error(f"Failed to set up job queue: {e}")
            logger.warning("Auto-updates will not work. Please install python-telegram-bot[job-queue]")
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(conv_handler)
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(CommandHandler("user_count", user_count))
        app.add_handler(CommandHandler("broadcast", broadcast))
        logger.info("Bot started")
        app.run_polling()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
