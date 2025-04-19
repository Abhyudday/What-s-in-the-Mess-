from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, time
import pytz

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Meal Timetable
meal_schedule = {
    "Breakfast": (time(7, 30), time(8, 30)),
    "Lunch": (time(12, 20), time(14, 0)),
    "Snacks": (time(17, 0), time(18, 0)),
    "Dinner": (time(19, 30), time(21, 0))
}

# New Menu Format with categories
menu = {
    "monday": {
        "Breakfast": {
            "Main Course": ["Veg Fried Idli", "Plain Idli"],
            "Dal & Curry": ["Sambhar"],
            "Extras": ["Coconut Chutney"],
            "Drinks": ["Tea", "Milk"],
            "Fruits": ["Seasonal Fruits"]
        },
        "Lunch": {
            "Main Course": ["Mix Veg with Paneer", "Rajma"],
            "Bread": ["Roti"],
            "Rice": ["Rice"],
            "Salads": ["Salad", "Boondi Raita", "Lemon 1/2"]
        },
        "Snacks": {
            "Main Course": ["Aloo Tikki", "Papdi Chaat (5 pc)", "Matar"],
            "Extras": ["Sonth", "Hari Chutney", "Chaat Masala"],
            "Drinks": ["Tea", "Curd"]
        },
        "Dinner": {
            "Dal & Curry": ["Arhar Dal", "Aloo Palak"],
            "Rice": ["Rice"],
            "Desserts": ["Suji Halwa / Kheer", "Moong Dal Halwa (once/month)"],
            "Salads": ["Onion Salad"]
        }
    },
    "tuesday": {
        "Breakfast": {
            "Main Course": ["Matar Kulche"],
            "Extras": ["Pickle"],
            "Drinks": ["Tea", "Milk"],
            "Fruits": ["Seasonal Fruits"]
        },
        "Lunch": {
            "Main Course": ["Tahari", "Aloo-Tamatar Curry"],
            "Bread": ["Roti"],
            "Salads": ["Salad", "Lemon 1/2", "Hari Chutney"],
            "Drinks": ["Curd"]
        },
        "Snacks": {
            "Main Course": ["Chowmein", "Pasta"],
            "Extras": ["Tomato Sauce", "Chili Sauce"],
            "Drinks": ["Coffee"]
        },
        "Dinner": {
            "Dal & Curry": ["Kali Masoor Dal", "Aloo Beans"],
            "Rice": ["Rice"],
            "Bread": ["Roti"],
            "Desserts": ["Ice Cream (Strawberry/Butterscotch/Chocolate/Mango)"],
            "Salads": ["Onion Salad"]
        }
    },
    # Add remaining days similarly...
}

def get_today_menu(meal_type):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A").lower()
    today_menu = menu.get(today, {}).get(meal_type)
    if not today_menu:
        return "No data available for this meal."

    lines = [f"*🍽️ {meal_type} Menu*"]
    for category, items in today_menu.items():
        emoji = {
            "Main Course": "🍛",
            "Dal & Curry": "🥘",
            "Rice": "🍚",
            "Bread": "🫓",
            "Salads": "🥗",
            "Desserts": "🍰",
            "Drinks": "☕",
            "Fruits": "🍎",
            "Extras": "🧂"
        }.get(category, "•")
        lines.append(f"\n*{emoji} {category}:*")
        for item in items:
            lines.append(f"  - {item}")
    return "\n".join(lines)

def get_next_meal():
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    for meal, (start, _) in meal_schedule.items():
        if now < start:
            return meal
    return "Breakfast (next day)"

def build_meal_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥣 Breakfast", callback_data="Breakfast")],
        [InlineKeyboardButton("🍛 Lunch", callback_data="Lunch")],
        [InlineKeyboardButton("🍪 Snacks", callback_data="Snacks")],
        [InlineKeyboardButton("🍽️ Dinner", callback_data="Dinner")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Mess Bot!\nClick below to check what’s in the mess now:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 What’s in Mess", callback_data="next_meal")]
        ])
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "next_meal":
        next_meal = get_next_meal()
        menu_text = get_today_menu(next_meal)
        await query.edit_message_text(
            menu_text,
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )
    elif query.data in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
        menu_text = get_today_menu(query.data)
        await query.edit_message_text(
            menu_text,
            parse_mode="Markdown",
            reply_markup=build_meal_buttons()
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🍽️ Mess Bot is live!")
    app.run_polling()
