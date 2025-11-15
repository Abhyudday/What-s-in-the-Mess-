from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, time, timedelta
import pytz
import os
import sys
import logging
import asyncio
import aiohttp
from db import init_db, save_user, get_all_users, update_notification_settings, get_user_settings, get_user_details, get_all_users_with_details
import psutil

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - get from environment variable (Railway secrets)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Validate bot token
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable is not set! Please set it in Railway secrets.")
    sys.exit(1)

# Track last notification sent to prevent duplicates
last_notification = {}

# Uptime monitoring URLs (you can add multiple services)
UPTIME_URLS = [
    # Add your actual uptime service URLs here
    # "https://uptime.betterstack.com/api/v1/heartbeat/your-heartbeat-id",
    # "https://api.uptimerobot.com/v2/getMonitors",
]

# Mess timetable
meal_schedule = {
    "Breakfast": (time(7, 30), time(8, 30)),
    "Lunch": (time(12, 20), time(14, 0)),
    "Snacks": (time(17, 0), time(18, 0)),
    "Dinner": (time(19, 30), time(21, 0))
}

# Boys Hostel Menu
boys_menu = {
    "Monday": {
        "Breakfast": "🍽️ Matar + Kulche + Milk + Tea + Fruit",
        "Lunch": "🍛 Mix Veg with Paneer + Arhar Dal + Rice + Roti + Boondi Raita + Salad + Lemon 1/2",
        "Snacks": "🥔 Aloo Patties + Tomato Chilli Sauce + Tea",
        "Dinner": "🍚 Rajma + Aloo Soyabean + Roti + Rice + Kheer/Sewai + Tomato Soup"
    },
    "Tuesday": {
        "Breakfast": "🍽️ Gobhi Paratha + Achar + Milk + Tea + Fruit",
        "Lunch": "🍛 Aloo Gobhi + Rajma + Roti + Rice + Curd + Salad + Lemon 1/2",
        "Snacks": "🍝 Macroni + Chilli & Tomato Sauce + Coffee",
        "Dinner": "🍚 Arhar Dal + Aloo Palak + Rice + Roti + Gulab Jamun + Sweetcorn Soup"
    },
    "Wednesday": {
        "Breakfast": "🍽️ Pav Bhaji + Butter + Tea + Milk + Fruit",
        "Lunch": "🍛 Aloo Pyaaj Sabji + Kadhi + Rice + Roti + Salad + Papad + Fried Lemon 1/2",
        "Snacks": "🥟 Mix Pakodi + Chilli & Tomato Sauce + Tea",
        "Dinner": "🍚 Plain Paratha + Kala Chana + Mix Veg + Rice + Custard + Veg Soup"
    },
    "Thursday": {
        "Breakfast": "🍽️ Aloo Pyaaj Paratha + Curd + Pickle + Tea + Fruit",
        "Lunch": "🍛 Aloo Methi + Chana Dal + Roti + Rice + Salad + Lemon 1/2 + Boondi Raita",
        "Snacks": "🍞 Bread Pakoda + Hari Chutney + Sonth + Tea",
        "Dinner": "🍚 Kadhi + Matar Paneer + Aloo Chokha + Jeera Rice + Roti/Puri + Masala Milk + Sirka Pyaaz"
    },
    "Friday": {
        "Breakfast": "🍽️ Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Fruit",
        "Lunch": "🍛 Chhole + Kashifal + Roti + Jeera Rice + Salad + Curd + Lemon 1/2",
        "Snacks": "🥙 Aloo Tikki / Chat Papdi + Tea",
        "Dinner": "🍚 Arhar Dal + Aloo Gobhi Matar + Sweetcorn Soup + Ice Cream (Butterscotch/Chocolate/Mango) + Matar Mushroom / Moong Dal Halwa (once in a month)"
    },
    "Saturday": {
        "Breakfast": "🍽️ Aloo Tamatar Sabji + Ajwain Puri + Tea + Jalebi + Curd + Pickle + Fruit",
        "Lunch": "🍛 Aloo Matar Gazar + Kali Masoor Dal + Tehri + Roti + Boondi Raita + Salad + Lemon 1/2",
        "Snacks": "🥟 Samosa + Tea + Hari Chutney",
        "Dinner": "🍚 Chhole + Aloo Patta Gobhi + Roti + Jeera Rice + Veg Soup"
    },
    "Sunday": {
        "Breakfast": "🍽️ Aloo Paratha + Hari Chutney (Tomato+Hari Dhaniya) + Tomato Sauce + Milk + Tea + Fruit",
        "Lunch": "🍛 Chhole + Bhature + Jeera Rice + Fry Mirchi + Sirka Pyaaz + Boondi Raita + Cold Drink + Achar",
        "Snacks": "🚫 OFF",
        "Dinner": "🍚 Arhar Dal + Aloo Matar + Rice + Roti + Tomato Soup + Coconut Laddoo/Gulab Jamun/Coconut Laddoo/Besan Laddoo (Alternate Basis)"
    }
}

# Girls Hostel Menu
girls_menu = {
    "Monday": {
        "Breakfast": "Matar with cucumber & onion + Kulcha + Tea ☕ + Milk + Fruit 🍎",
        "Lunch": "Arhar Daal + Mix veg with paneer + Boondi raita + Rice 🍚 + Chapati + Salad 🥗 + 1/2 Lemon 🍋",
        "Snacks": "Bread pakoda/Mix pakodi + Tomato sauce + Green chutni + Tea ☕ (Green elaichi)",
        "Dinner": "Butter masala/Matar paneer + Aloo chokha + Chapati + Rice + Bessan Laddu/Jalebi + Masala chaach 🍬"
    },
    "Tuesday": {
        "Breakfast": "Fried idli + Sambhar + Nariyal chutni + Tea ☕ + Milk + Fruit 🍌",
        "Lunch": "Rajma + French beans + Aloo tamatar + Rice 🍚 + Curd + Salad 🥗 + 1/2 Lemon 🍋",
        "Snacks": "Chowmein + Tomato & green chilli sauce + Tang 🥤",
        "Dinner": "Tamatar-Aloo-Paneer + Chapati + Rice 🍚 + Gulab jamun 🍩 + Chaach"
    },
    "Wednesday": {
        "Breakfast": "Bread + Amul butter + Jam + Cornflakes + Tea ☕ + Milk + Fruit 🍇",
        "Lunch": "Kadhi + Aloo jeera + Chapati + Rice 🍚 + Fried mirchi + Papad + Masala onion + Lemon 🍋",
        "Snacks": "Poha/Namkeen jave + Sauce + Roohafza 🥤",
        "Dinner": "Matar chhole + Aloo tikki + Curd + Rice 🍚 OR Dum aloo/Mix veg + Ice cream 🍨"
    },
    "Thursday": {
        "Breakfast": "Plain parantha + Aloo jeera + Tea ☕ + Milk + Fruit 🍊",
        "Lunch": "Arhar daal + Aloo baingan + Rice 🍚 + Salad 🥗 + Lemon 🍋",
        "Snacks": "Macaroni + Sauce + Roohafza 🥤",
        "Dinner": "Chhole + Aloo tamatar + Chapati + Rice 🍚 + Ice cream 🍨 + Salad"
    },
    "Friday": {
        "Breakfast": "Pav bhaji + Tea ☕ + Milk + Fruit 🍐",
        "Lunch": "Rajma + Aloo jeera + Meethi (pasaa) + Rice 🍚 + Curd + Salad 🥗",
        "Snacks": "Black chana chaat + Coffee ☕",
        "Dinner": "Lauki kofta + Masoor daal + Veg curry + Rice 🍚 + Chapati + Ice cream 🍨 OR Methi aloo + Salad"
    },
    "Saturday": {
        "Breakfast": "Aloo parantha + Green chutni + Tea ☕ + Milk + Pickle + Fruit 🍎",
        "Lunch": "Black chana + Lauki kofta + Chapati + Rice 🍚 + Veg raita + Salad 🥗 + Lemon 🍋",
        "Snacks": "Samosa + Saunth + Green chutni + Tea ☕",
        "Dinner": "Pulav + Dahi aloo + Salad 🥗 + Custard 🍮 + Masala chaach"
    },
    "Sunday": {
        "Breakfast": "Aloo tamatar sabji + Poori + Tea ☕ + Milk + Pickle + Fruit 🍌",
        "Lunch": "Chhole masala + Aloo pyaz + Chapati + Rice 🍚 + Boondi raita + Salad 🥗 + Lemon 🍋",
        "Snacks": "OFF ❌",
        "Dinner": "Lauki chana daal + Arbi + Chapati + Rice 🍚 + Fruit + Custard 🍮 + Masala chaach"
    }
}

# Check if bot is already running
def is_bot_running():
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

# Store the current menu selection in user_data
def get_menu_for_user(user_id):
    return context.user_data.get('selected_hostel', 'boys')

def build_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Select Hostel", callback_data="select_hostel")],
        [InlineKeyboardButton("🍽️ Today's Menu", callback_data="next_meal")],
        [InlineKeyboardButton("📅 View Other Days", callback_data="choose_day")],
        [InlineKeyboardButton("🔔 Notifications", callback_data="notification_settings")]
    ])

def build_notification_buttons(user_id):
    settings = get_user_settings(user_id)
    is_enabled = settings[1] if settings else False
    status_emoji = "✅" if is_enabled else "❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{status_emoji} 15-min Notifications: {'ON' if is_enabled else 'OFF'}", callback_data="toggle_updates")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
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
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ])

def build_day_buttons():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    kb = []
    for i in range(0, len(days), 2):
        row = [InlineKeyboardButton(days[i], callback_data=f"day_{days[i]}")]
        if i + 1 < len(days):
            row.append(InlineKeyboardButton(days[i + 1], callback_data=f"day_{days[i + 1]}"))
        kb.append(row)
    kb.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")])
    return InlineKeyboardMarkup(kb)

def build_time_buttons():
    times = ["5", "10", "15", "20", "30", "45", "60", "Custom"]
    kb = []
    for i in range(0, len(times), 3):
        row = [InlineKeyboardButton(f"{t} min", callback_data=f"time_{t}") for t in times[i:i+3]]
        kb.append(row)
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    return InlineKeyboardMarkup(kb)

def build_hostel_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👨 Boys Hostel", callback_data="hostel_boys"),
            InlineKeyboardButton("👩 Girls Hostel", callback_data="hostel_girls")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ])

async def save_user_info(update: Update):
    """Save user information to database"""
    user = update.effective_user
    if user:
        save_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await save_user_info(update)
    await update.message.reply_text(
        "👋 Welcome to the Mess Bot!\n\n"
        "🍽️ Check today's menu or view other days\n"
        "🔔 Get notified 15 minutes before each meal\n\n"
        "What would you like to do?",
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
    
    # Get all users with auto-updates enabled
    all_users = get_all_users()
    
    for user_id in all_users:
        settings = get_user_settings(user_id)
        if not settings or not settings[1]:  # settings[1] is auto_updates
            continue
            
        # Create a unique key for this notification
        notification_key = f"{user_id}_{today}_{next_meal}"
        
        # Only send if we're within 1 minute of the notification time and haven't sent this notification before
        if (abs((now - notification_time).total_seconds()) <= 60 and 
            notification_key not in last_notification):
            
            message = f"🔔 *Upcoming {next_meal} in 15 minutes!*\n\n🍽️ *{today}'s {next_meal} Menu:*\n\n{menu[today].get(next_meal,'No data')}"
            
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown"
                )
                # Mark this notification as sent
                last_notification[notification_key] = now
            except Exception as e:
                logger.error(f"Failed to send notification to {user_id}: {e}")
    
    # Clean up old notification records
    last_notification.clear()

# Simple uptime ping to keep the bot alive
async def simple_uptime_ping():
    """Simple uptime ping to keep the bot alive"""
    try:
        # Just log that we're alive
        logger.info("🔄 Bot is alive and running - uptime ping sent")
    except Exception as e:
        logger.error(f"Failed to send simple uptime ping: {e}")

async def uptime_ping():
    """Send ping to uptime monitoring services to keep the bot alive"""
    # Always send simple ping
    await simple_uptime_ping()
    
    # Send pings to external services if configured
    if UPTIME_URLS:
        async with aiohttp.ClientSession() as session:
            for url in UPTIME_URLS:
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            logger.info(f"✅ Uptime ping successful to {url}")
                        else:
                            logger.warning(f"⚠️ Uptime ping failed to {url} with status {response.status}")
                except Exception as e:
                    logger.error(f"❌ Failed to ping {url}: {e}")
    else:
        logger.info("ℹ️ No external uptime services configured - using simple ping only")

async def uptime_job(context: ContextTypes.DEFAULT_TYPE):
    """Job to send uptime pings every 5 minutes"""
    await uptime_ping()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id

    # Handle hostel selection
    if data == "select_hostel":
        await query.edit_message_text(
            "🏠 *Select your hostel:*",
            parse_mode="Markdown",
            reply_markup=build_hostel_buttons()
        )
        return

    if data.startswith("hostel_"):
        hostel = data.split("_")[1]
        context.user_data['selected_hostel'] = hostel
        await query.edit_message_text(
            f"✅ Selected {hostel.title()} Hostel!\n\nWhat would you like to do?",
            reply_markup=build_main_buttons()
        )
        return

    # Handle notification settings
    if data == "notification_settings":
        settings = get_user_settings(user_id)
        is_enabled = settings[1] if settings else False
        status_emoji = "✅" if is_enabled else "❌"
        await query.edit_message_text(
            "🔔 *Notification Settings*\n\n"
            "Get notified 15 minutes before each meal time.\n"
            "Toggle the button below to enable/disable notifications.",
            parse_mode="Markdown",
            reply_markup=build_notification_buttons(user_id)
        )
        return

    # Handle auto-update toggle
    if data == "toggle_updates":
        settings = get_user_settings(user_id)
        current_status = settings[1] if settings else False
        
        update_notification_settings(user_id, auto_updates=not current_status)
        status = "enabled" if not current_status else "disabled"
        
        await query.edit_message_text(
            f"🔔 *Notification Settings*\n\n"
            f"Notifications have been {status}!\n"
            f"You will receive notifications 15 minutes before each meal.",
            parse_mode="Markdown",
            reply_markup=build_notification_buttons(user_id)
        )
        return

    # clear selection if we go back
    if data == "back_to_main":
        context.user_data.pop("selected_day", None)
        await query.edit_message_text(
            "👋 Welcome back! What would you like to do?",
            reply_markup=build_main_buttons()
        )
        return

    # next_meal on main
    if data == "next_meal":
        context.user_data.pop("selected_day", None)
        meal = get_current_or_next_meal()
        today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A")
        hostel = context.user_data.get('selected_hostel', 'boys')
        menu = boys_menu if hostel == 'boys' else girls_menu
        text = f"🍽️ *{today}'s {meal} Menu ({hostel.title()} Hostel):*\n\n{menu[today].get(meal,'No data')}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_meal_buttons())
        return

    # choose day
    if data == "choose_day":
        await query.edit_message_text(
            "📅 *Choose a day to view its menu:*",
            parse_mode="Markdown",
            reply_markup=build_day_buttons()
        )
        return

    # day selected
    if data.startswith("day_"):
        day = data.split("_",1)[1]
        context.user_data["selected_day"] = day
        # show that day's current/next meal
        meal = get_current_or_next_meal()
        hostel = context.user_data.get('selected_hostel', 'boys')
        menu = boys_menu if hostel == 'boys' else girls_menu
        text = f"🍽️ *{day}'s {meal} Menu ({hostel.title()} Hostel):*\n\n{menu[day].get(meal,'No data')}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_meal_buttons())
        return

    # meal button (Breakfast/Lunch/Snacks/Dinner)
    if data in meal_schedule:
        # if a day was chosen, use that, otherwise today
        day = context.user_data.get("selected_day") or datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A")
        hostel = context.user_data.get('selected_hostel', 'boys')
        menu = boys_menu if hostel == 'boys' else girls_menu
        text = f"🍽️ *{day}'s {data} Menu ({hostel.title()} Hostel):*\n\n{menu[day].get(data,'No data')}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=build_meal_buttons())
        return

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a personalized broadcast message to all users"""
    if not context.args:
        await update.message.reply_text(
            "Please provide a message to broadcast.\n\n"
            "Personalization variables:\n"
            "• <user name> - User's first name\n"
            "• <username> - User's username\n"
            "• <full name> - User's full name\n\n"
            "Examples:\n"
            "• /broadcast Hi <user name>, how are you?\n"
            "• /broadcast Hello @<username>, check out the new menu!\n"
            "• /broadcast Good morning <full name>! 🌅"
        )
        return
        
    message_template = " ".join(context.args)
    users = get_all_users()
    success = 0
    failed = 0
    user_details = []
    
    for user_id in users:
        try:
            # Get user details for personalization
            user_info = get_user_details(user_id)
            if user_info:
                first_name = user_info.get('first_name', 'User')
                last_name = user_info.get('last_name', '')
                username = user_info.get('username', 'user')
                full_name = f"{first_name} {last_name}".strip()
                
                # Personalize the message with multiple variables
                personalized_message = message_template
                personalized_message = personalized_message.replace('<user name>', first_name)
                personalized_message = personalized_message.replace('<username>', username)
                personalized_message = personalized_message.replace('<full name>', full_name)
                
                user_details.append(f"✅ {first_name} (@{username})")
            else:
                personalized_message = message_template
                personalized_message = personalized_message.replace('<user name>', 'User')
                personalized_message = personalized_message.replace('<username>', 'user')
                personalized_message = personalized_message.replace('<full name>', 'User')
                user_details.append(f"✅ User {user_id}")
            
            await context.bot.send_message(
                chat_id=user_id,
                text=personalized_message,
                parse_mode="Markdown"
            )
            success += 1
            
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
            failed += 1
            user_details.append(f"❌ User {user_id} (Failed)")
    
    # Create detailed report
    report = f"📢 *Personalized Broadcast Report*\n\n"
    report += f"📝 *Message Template:* {message_template}\n\n"
    report += f"📊 *Summary:*\n"
    report += f"✅ Successfully sent: {success}\n"
    report += f"❌ Failed: {failed}\n"
    report += f"📋 *Recipients:*\n"
    
    # Add user details (limit to first 20 to avoid message too long)
    for i, detail in enumerate(user_details[:20]):
        report += f"{detail}\n"
    
    if len(user_details) > 20:
        report += f"... and {len(user_details) - 20} more users\n"
    
    await update.message.reply_text(report, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom time input"""
    if context.user_data.get('waiting_for_custom_time'):
        try:
            minutes = int(update.message.text)
            if 1 <= minutes <= 1440:  # Allow up to 24 hours
                user_id = update.effective_user.id
                update_notification_settings(user_id, notification_time=minutes)
                await update.message.reply_text(
                    f"✅ Notification time set to {minutes} minutes before each meal!",
                    reply_markup=build_main_buttons()
                )
            else:
                await update.message.reply_text(
                    "Please enter a number between 1 and 1440 minutes.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back", callback_data="set_notification_time")
                    ]])
                )
        except ValueError:
            await update.message.reply_text(
                "Please enter a valid number.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data="set_notification_time")
                ]])
            )
        context.user_data.pop('waiting_for_custom_time', None)
        return

async def get_user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hidden command to get total number of users"""
    users = get_all_users()
    await update.message.reply_text(f"👥 Total users: {len(users)}")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hidden command to list all users with their details"""
    users = get_all_users_with_details()
    
    if not users:
        await update.message.reply_text("📋 No users found in the database.")
        return
    
    report = f"📋 *User List ({len(users)} users)*\n\n"
    
    for i, user in enumerate(users, 1):
        name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        username = user.get('username', 'No username')
        auto_updates = "✅" if user.get('auto_updates') else "❌"
        
        full_name = f"{name} {last_name}".strip()
        report += f"{i}. {full_name} (@{username}) {auto_updates}\n"
        
        # Split into multiple messages if too long
        if i % 15 == 0 and i < len(users):
            await update.message.reply_text(report, parse_mode="Markdown")
            report = ""
    
    if report:
        await update.message.reply_text(report, parse_mode="Markdown")

if __name__ == "__main__":
    try:
        # Initialize database with error handling
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.warning("Bot will run without database functionality")
        
        # Check if bot is already running
        if is_bot_running():
            print("Bot is already running! Exiting...")
            sys.exit(1)
            
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Add job to check for notifications every minute
        try:
            job_queue = app.job_queue
            if job_queue is not None:
                job_queue.run_repeating(send_meal_notification, interval=60, first=10)
                # Add uptime ping job every 5 minutes
                job_queue.run_repeating(uptime_job, interval=300, first=30)  # 5 minutes = 300 seconds
                logger.info("Job queue started successfully")
            else:
                logger.warning("Job queue is not available. Auto-updates will not work.")
        except Exception as e:
            logger.error(f"Failed to set up job queue: {e}")
            logger.warning("Auto-updates will not work. Please install python-telegram-bot[job-queue]")
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(CommandHandler("broadcast", broadcast))
        app.add_handler(CommandHandler("kitne", get_user_count))
        app.add_handler(CommandHandler("list_users", list_users))
        logger.info("Bot started with uptime monitoring")
        app.run_polling()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
