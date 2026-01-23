import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Google Ads
GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")

# Settings
REPORT_INTERVAL_HOURS = int(os.getenv("REPORT_INTERVAL_HOURS", 1))
TIMEZONE = os.getenv("TIMEZONE", "Europe/Rome")

# Campaign settings
CAMPAIGN_NAME = "Luxury_Cars_EN"
DAILY_BUDGET = 80.0

# Alert thresholds
CTR_WARNING_THRESHOLD = 1.0  # Alert if CTR < 1%
CPC_WARNING_THRESHOLD = 5.0  # Alert if CPC > €5
SPEND_WARNING_PERCENT = 90   # Alert if spend > 90% of budget
