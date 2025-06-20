# Mess Menu Telegram Bot

A Telegram bot that provides mess menu information and notifications for meal times for both boys' and girls' hostels.

## Features

- View today's menu for both boys' and girls' hostels
- Get notifications 15 minutes before each meal
- Auto-updates for all meals
- Persistent storage using PostgreSQL
- Uptime monitoring to prevent sleep on Railway free tier
- Broadcast messages to all users

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Abhyudday/What-s-in-the-Mess-.git
cd What-s-in-the-Mess-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (for Railway deployment):
   - `BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `DATABASE_URL`: Railway automatically provides this for PostgreSQL

4. Configure uptime monitoring (see section below)

5. Run the bot:
```bash
python main.py
```

## Railway Deployment

### Environment Variables
Railway automatically handles most configuration, but you need to set:

1. **BOT_TOKEN**: Your Telegram bot token
   - Get it from @BotFather on Telegram
   - Set it in Railway secrets/environment variables

2. **DATABASE_URL**: Automatically provided by Railway when you add PostgreSQL

### Deployment Steps
1. Connect your GitHub repository to Railway
2. Add PostgreSQL database service
3. Set the `BOT_TOKEN` environment variable
4. Deploy the application

## Uptime Monitoring Setup

To prevent your bot from sleeping on Railway's free tier, set up uptime monitoring:

### Option 1: Built-in Uptime Monitoring (Recommended)
The bot includes built-in uptime monitoring that pings every 5 minutes. Update the `UPTIME_URLS` in `main.py` with your actual uptime service URLs.

### Option 2: External Uptime Services
Use free uptime monitoring services:

1. **UptimeRobot** (Free tier available):
   - Sign up at https://uptimerobot.com
   - Add your Railway app URL
   - Set monitoring interval to 5 minutes

2. **BetterStack** (Free tier available):
   - Sign up at https://betterstack.com
   - Create a heartbeat for your Railway app
   - Update the URL in `main.py`

3. **Cron-job.org** (Free):
   - Sign up at https://cron-job.org
   - Create a cron job to ping your Railway app every 5 minutes

4. **Cronitor** (Free tier available):
   - Sign up at https://cronitor.io
   - Create a monitor for your Railway app

### Option 3: Standalone Uptime Script
Run the `uptime.py` script separately:
```bash
python uptime.py
```

Update the URLs in `uptime.py` with your actual Railway app URL and uptime service URLs.

## Configuration

### Local Development
For local development, you can set environment variables in a `.env` file:
```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=your_database_url
```

### Railway Deployment
Railway automatically handles environment variables through their dashboard:
- Go to your Railway app settings
- Add environment variables in the "Variables" tab
- Railway automatically provides `DATABASE_URL` for PostgreSQL

## Usage

1. Start the bot by sending `/start` in Telegram
2. Select your hostel (Boys or Girls)
3. Use the menu buttons to:
   - View today's menu
   - View menu for specific days
   - Enable/disable notifications
   - View specific meals

## Commands

- `/start` - Start the bot
- `/broadcast <message>` - Send a message to all users (admin only)
- `/kitne` - Get total number of users (hidden command)

## Meal Times

- **Breakfast**: 7:30 AM - 8:30 AM
- **Lunch**: 12:20 PM - 2:00 PM
- **Snacks**: 5:00 PM - 6:00 PM
- **Dinner**: 7:30 PM - 9:00 PM

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 