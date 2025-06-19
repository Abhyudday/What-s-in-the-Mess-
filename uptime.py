"""
Simple uptime monitoring script for Railway free tier
This script sends periodic pings to keep your bot alive
"""

import requests
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your Railway app URL (replace with your actual URL)
RAILWAY_APP_URL = "https://your-app-name.railway.app"  # Replace with your actual Railway URL

# Free uptime monitoring services
UPTIME_SERVICES = [
    "https://uptime.betterstack.com/api/v1/heartbeat/your-heartbeat-id",  # Replace with your BetterStack URL
    "https://api.uptimerobot.com/v2/getMonitors",  # UptimeRobot
    "https://cron-job.org/api/cronjob/your-cronjob-id",  # Cron-job.org
    "https://api.cronitor.io/v3/monitors/your-monitor-id/ping",  # Cronitor
]

def ping_uptime_services():
    """Send ping to uptime monitoring services"""
    for service in UPTIME_SERVICES:
        try:
            response = requests.get(service, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Ping successful to {service}")
            else:
                logger.warning(f"⚠️ Ping failed to {service} with status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Failed to ping {service}: {e}")

def ping_railway_app():
    """Ping your Railway app directly"""
    try:
        response = requests.get(RAILWAY_APP_URL, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Railway app ping successful")
        else:
            logger.warning(f"⚠️ Railway app ping failed with status {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Failed to ping Railway app: {e}")

def main():
    """Main function to run uptime monitoring"""
    logger.info("🚀 Starting uptime monitoring...")
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"⏰ {current_time} - Sending uptime pings...")
            
            # Ping Railway app
            ping_railway_app()
            
            # Ping uptime services
            ping_uptime_services()
            
            logger.info("💤 Sleeping for 5 minutes...")
            time.sleep(300)  # Sleep for 5 minutes
            
        except KeyboardInterrupt:
            logger.info("🛑 Uptime monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in uptime monitoring: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main() 