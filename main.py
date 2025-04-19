from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, time
import pytz

BOT_TOKEN = "7265497857:AAFAfZEgGwMlA3GTR3xQv7G-ah0-hoA8jVQ"

# Meal timings (IST)
meal_schedule = {
    "Breakfast": (time(7, 30), time(8, 30)),
    "Lunch": (time(12, 20), time(14, 0)),
    "Snacks": (time(17, 0), time(18, 0)),
    "Dinner": (time(19, 30), time(21, 0))
}

# Full menu with nutritional information
menu = {
    "monday": {
        "Breakfast": {
            "items": "Veg Fried Idli + Plain Idli + Sambhar + Coconut Chutney + Tea + Milk + Seasonal Fruits",
            "nutrition": "Calories: 350 | Protein: 10g | Carbs: 60g | Fats: 10g"
        },
        "Lunch": {
            "items": "Mix Veg with Paneer + Rajma + Roti (3) + Rice + Salad + Boondi Raita + Lemon 1/2",
            "nutrition": "Calories: 500 | Protein: 15g | Carbs: 80g | Fats: 18g"
        },
        "Snacks": {
            "items": "Aaloo Tikki/Papdi Chat (5 pc) + Matar + Curd + Sonth + Hari Chutney + Tea",
            "nutrition": "Calories: 250 | Protein: 7g | Carbs: 40g | Fats: 10g"
        },
        "Dinner": {
            "items": "Arhar Dal + Aloo Palak + Rice + Suji Halwa / Kheer + Onion Salad",
            "nutrition": "Calories: 450 | Protein: 12g | Carbs: 70g | Fats: 15g"
        }
    },
    "tuesday": {
        "Breakfast": {
            "items": "Matar Kulche + Pickle + Tea + Milk + Seasonal Fruits",
            "nutrition": "Calories: 400 | Protein: 12g | Carbs: 65g | Fats: 15g"
        },
        "Lunch": {
            "items": "Tahari + Aloo Tamatar Sabji + Roti (3) + Salad + Curd + Lemon 1/2 + Hari Chutney",
            "nutrition": "Calories: 550 | Protein: 14g | Carbs: 85g | Fats: 18g"
        },
        "Snacks": {
            "items": "Chowmein / Pasta + Tomato Sauce + Chili Sauce + Coffee",
            "nutrition": "Calories: 300 | Protein: 8g | Carbs: 50g | Fats: 12g"
        },
        "Dinner": {
            "items": "Kali Massor Dal + Aloo Beans + Rice + Roti (3) + Ice Cream + Onion Salad",
            "nutrition": "Calories: 550 | Protein: 20g | Carbs: 75g | Fats: 18g"
        }
    },
    "wednesday": {
        "Breakfast": {
            "items": "Plain Paratha + Aloo Tamater Sabji + Pickle + Tea + Milk + Seasonal Fruits",
            "nutrition": "Calories: 400 | Protein: 10g | Carbs: 60g | Fats: 15g"
        },
        "Lunch": {
            "items": "Kaabli Chole + Kashifal + Roti (3) + Jeera Rice + Mix Salad + Curd + Lemon 1/2",
            "nutrition": "Calories: 500 | Protein: 18g | Carbs: 85g | Fats: 16g"
        },
        "Snacks": {
            "items": "Samosa + Chili Sauce + Sonth + Tea",
            "nutrition": "Calories: 200 | Protein: 5g | Carbs: 30g | Fats: 10g"
        },
        "Dinner": {
            "items": "(Mattar/Kadahi) Paneer + Aloo Began Tomato Chokha + Puri + Pulaw + Onion Salad",
            "nutrition": "Calories: 600 | Protein: 20g | Carbs: 80g | Fats: 20g"
        }
    },
    "thursday": {
        "Breakfast": {
            "items": "Pav Bhaji + Tea + Milk + Butter + Seasonal Fruits",
            "nutrition": "Calories: 400 | Protein: 10g | Carbs: 65g | Fats: 15g"
        },
        "Lunch": {
            "items": "Aloo Pyaaj + Kadhi + Rice + Roti (3) + Salad + Fried Papad + Lemon 1/2",
            "nutrition": "Calories: 500 | Protein: 12g | Carbs: 80g | Fats: 20g"
        },
        "Snacks": {
            "items": "Bread Pakoda / Rusk (6 pcs) + Sonath + Hari Chutney + Tea",
            "nutrition": "Calories: 250 | Protein: 6g | Carbs: 40g | Fats: 12g"
        },
        "Dinner": {
            "items": "Aloo Gobhi Mattar with Gravy + Chana Dal + Roti (3) + Rice + Gulab Jamun + Onion Salad",
            "nutrition": "Calories: 550 | Protein: 18g | Carbs: 75g | Fats: 20g"
        }
    },
    "friday": {
        "Breakfast": {
            "items": "Aloo Pyaj Paratha + Pickle + Curd + Tea + Seasonal Fruits",
            "nutrition": "Calories: 450 | Protein: 12g | Carbs: 60g | Fats: 18g"
        },
        "Lunch": {
            "items": "Aloo Gobhi Mattar + Arhar Dal + Roti (3) + Rice + Mix Salad + Boondi Raita + Lemon 1/2",
            "nutrition": "Calories: 550 | Protein: 16g | Carbs: 85g | Fats: 18g"
        },
        "Snacks": {
            "items": "Patties + Tomato Sauce + Coffee",
            "nutrition": "Calories: 250 | Protein: 6g | Carbs: 40g | Fats: 12g"
        },
        "Dinner": {
            "items": "Lauki Kofta + Mix Veg + Arhar Dal + Aloo Soyabeen + Onion Rice + Roti + Besan Ladoo + Onion Salad",
            "nutrition": "Calories: 650 | Protein: 20g | Carbs: 85g | Fats: 25g"
        }
    },
    "saturday": {
        "Breakfast": {
            "items": "Aloo Tamatar Sabji + Ajwain Poori + Fry Mirchi + Tea + Jalebi + Curd + Seasonal Fruits",
            "nutrition": "Calories: 500 | Protein: 14g | Carbs: 75g | Fats: 20g"
        },
        "Lunch": {
            "items": "Louki Fry + Arhar Dal + Roti (3) + Rice + Salad + Curd + Lemon 1/2",
            "nutrition": "Calories: 550 | Protein: 15g | Carbs: 80g | Fats: 20g"
        },
        "Snacks": {
            "items": "Namkeen Jave / Poha + Chili Sauce + Tomato Sauce + Coffee",
            "nutrition": "Calories: 300 | Protein: 7g | Carbs: 45g | Fats: 12g"
        },
        "Dinner": {
            "items": "Rajma + Aloo Bhujia + Jeera Rice + Roti + Onion Salad",
            "nutrition": "Calories: 500 | Protein: 15g | Carbs: 80g | Fats: 18g"
        }
    },
    "sunday": {
        "Breakfast": {
            "items": "Rosted Bread + Aloo Sandwich + Tomato Sauce + Cornflakes + Milk + Tea + Seasonal Fruits",
            "nutrition": "Calories: 400 | Protein: 12g | Carbs: 60g | Fats: 15g"
        },
        "Lunch": {
            "items": "Chole (Kabuli Chane Big) + Bhature + Fried Mirch + Sirka Pyaaz + Jeera Rice + Cold Drink + Pickle + Veg Raita",
            "nutrition": "Calories: 600 | Protein: 20g | Carbs: 90g | Fats: 25g"
        },
        "Snacks": {
            "items": "OFF",
            "nutrition": "N/A"
        },
        "Dinner": {
            "items": "Mix Dal + Aloo Kala Chana + Roti (3) + Rice + Sewai + Onion Salad",
            "nutrition": "Calories: 500 | Protein: 18g | Carbs: 75g | Fats: 15g"
        }
    }
}

# Suggestion storage (in memory for now)
suggestions = []

def get_today_menu(meal_type):
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%A").lower()
    return menu.get(today, {}).get(meal_type, {"items": "No data for this meal.", "nutrition": "N/A"})

def get_next_meal():
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    for meal, (start, end) in meal_schedule.items():
        if now < start:
            return meal, start
        elif now < end:
            return meal, start
    return "No more meals today", time(23, 59)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Breakfast", callback_data="breakfast"),
         InlineKeyboardButton("Lunch", callback_data="lunch")],
        [InlineKeyboardButton("Snacks", callback_data="snacks"),
         InlineKeyboardButton("Dinner", callback_data="dinner")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a meal to see today's menu.", reply_markup=reply_markup)

async def show_meal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    meal_type = query.data.lower()
    meal_info = get_today_menu(meal_type)
    
    meal_msg = f"Today's {meal_type.capitalize()}:\n{meal_info['items']}\nNutritional Info: {meal_info['nutrition']}"
    
    await query.answer()
    await query.edit_message_text(text=meal_msg)

async def suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    meal, _ = get_next_meal()
    suggestions.append(meal)
    await update.message.reply_text(f"Suggested meal for next time: {meal}.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_meal))
    application.add_handler(CommandHandler("suggest", suggestion))

    application.run_polling()

if __name__ == '__main__':
    main()
