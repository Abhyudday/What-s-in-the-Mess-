# Mess Menu Telegram Bot

A Telegram bot that provides mess menu information and notifications for meal times.

## Features

- View today's menu
- Get notifications before or after meal times
- Customizable notification timing
- Auto-updates for all meals
- Persistent storage using Redis

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mess-menu-bot.git
cd mess-menu-bot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_user_id
REDIS_URL=your_redis_url
```

5. Run the bot:
```bash
python main.py
```

## Usage

1. Start the bot by sending `/start` in Telegram
2. Use the menu buttons to:
   - View today's menu
   - Enable/disable auto-updates
   - Set notification timing
   - View menu for specific days

## Notification Settings

- Use negative numbers (e.g., -15) to get notified before the meal
- Use positive numbers (e.g., 15) to get notified after the meal starts
- Range: -60 to 60 minutes (excluding 0)

## Contributing

Feel free to submit issues and enhancement requests! 