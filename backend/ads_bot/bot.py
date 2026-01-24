"""
Prestige Cars 24 - Google Ads Telegram Bot
"""
import logging
from functools import wraps
from datetime import datetime
from typing import Optional

import pytz
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import config
from google_ads_client import ads_manager

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Allowed users
ALLOWED_USERS = [675639837, 771081107, 8477058203]

# Scheduler
scheduler = AsyncIOScheduler(timezone=pytz.timezone(config.TIMEZONE))
is_monitoring = False


# === Decorator ===
def restricted(func):
    """Decorator to restrict access to allowed users only"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            await update.message.reply_text("⛔ Access denied")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


# === Helpers ===
def format_currency(value: float) -> str:
    return f"€{value:.2f}"

def format_percent(value: float) -> str:
    return f"{value:.2f}%"

def get_progress_bar(current: float, total: float, length: int = 10) -> str:
    if total == 0:
        return "░" * length
    percent = min(current / total, 1.0)
    filled = int(length * percent)
    return "█" * filled + "░" * (length - filled)


async def generate_report() -> str:
    """Generate hourly report"""
    stats = ads_manager.get_today_stats()
    ad_groups = ads_manager.get_ad_group_stats()
    
    if not stats:
        return "❌ Failed to fetch statistics"
    
    now = datetime.now(pytz.timezone(config.TIMEZONE))
    budget_percent = (stats["cost"] / config.DAILY_BUDGET) * 100
    
    report = f"""
📊 *PRESTIGE CARS 24 — Report*
🕐 {now.strftime("%d %b %Y, %H:%M")}

━━━━━━━━━━━━━━━━━━━━━━

💰 *Budget:* {format_currency(stats["cost"])} / {format_currency(config.DAILY_BUDGET)}
{get_progress_bar(stats["cost"], config.DAILY_BUDGET, 15)} {budget_percent:.0f}%

📈 *Metrics:*
├ 👁 Impressions: {stats["impressions"]:,}
├ 👆 Clicks: {stats["clicks"]}
├ 📊 CTR: {format_percent(stats["ctr"])}
├ 💵 Avg CPC: {format_currency(stats["avg_cpc"])}
└ 🎯 Conversions: {stats["conversions"]}

🏆 *Top Ad Groups:*"""
    
    for i, ag in enumerate(ad_groups[:5], 1):
        report += f"\n{i}. {ag['name']}: {ag['clicks']} clicks, {format_currency(ag['cost'])}"
    
    alerts = []
    if stats["ctr"] < config.CTR_WARNING_THRESHOLD and stats["impressions"] > 100:
        alerts.append(f"⚠️ Low CTR: {format_percent(stats['ctr'])}")
    if stats["avg_cpc"] > config.CPC_WARNING_THRESHOLD:
        alerts.append(f"⚠️ High CPC: {format_currency(stats['avg_cpc'])}")
    if budget_percent > config.SPEND_WARNING_PERCENT:
        alerts.append(f"⚠️ Budget {budget_percent:.0f}% spent")
    
    if alerts:
        report += "\n\n🚨 *Alerts:*"
        for alert in alerts[:5]:
            report += f"\n{alert}"
    else:
        report += "\n\n✅ All metrics within normal range"
    
    report += f"\n\n📍 Status: {stats['status']}"
    return report


async def send_scheduled_report(context: ContextTypes.DEFAULT_TYPE):
    """Send scheduled report to all allowed users"""
    try:
        report = await generate_report()
        for chat_id in ALLOWED_USERS:
            try:
                await context.bot.send_message(chat_id=chat_id, text=report, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to send to {chat_id}: {e}")
        logger.info("Scheduled report sent")
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        

@restricted
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_monitoring
    chat_id = update.effective_chat.id
    
    welcome = f"""
🚗 *Prestige Cars 24 - Ads Monitor*

*Commands:*
/report - Get report now
/status - Campaign status
/adgroups - Ad groups performance
/keywords - Top search terms
/pause - Pause campaign
/enable - Enable campaign
/start - Start monitoring
/stop - Stop monitoring
/help - Show all commands
"""
    await update.message.reply_text(welcome, parse_mode="Markdown")
    
    if not is_monitoring:
        scheduler.add_job(
            send_scheduled_report,
            trigger=IntervalTrigger(hours=config.REPORT_INTERVAL_HOURS),
            id="hourly_report", replace_existing=True, args=[context]
        )
        if not scheduler.running:
            scheduler.start()
        is_monitoring = True
        await update.message.reply_text(f"✅ Monitoring started! Reports every {config.REPORT_INTERVAL_HOURS}h")


@restricted
async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_monitoring
    if is_monitoring:
        scheduler.remove_job("hourly_report")
        is_monitoring = False
        await update.message.reply_text("⏹ Monitoring stopped.")
    else:
        await update.message.reply_text("ℹ️ Monitoring is not active.")


@restricted
async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Generating report...")
    report = await generate_report()
    await update.message.reply_text(report, parse_mode="Markdown")


@restricted
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = ads_manager.get_today_stats()
    if not stats:
        await update.message.reply_text("❌ Failed to fetch status")
        return
    text = f"""📍 *Campaign Status*
Campaign: {stats["campaign_name"]}
Status: {stats["status"]}
Spend: {format_currency(stats["cost"])} / {format_currency(config.DAILY_BUDGET)}
Clicks: {stats["clicks"]} | Conversions: {stats["conversions"]}"""
    await update.message.reply_text(text, parse_mode="Markdown")


@restricted
async def cmd_adgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ad_groups = ads_manager.get_ad_group_stats()
    if not ad_groups:
        await update.message.reply_text("❌ No data available")
        return
    text = "📊 *Ad Groups (Today)*\n\n"
    for ag in ad_groups:
        emoji = "🟢" if ag["ctr"] >= 1.0 else "🟡" if ag["ctr"] >= 0.5 else "🔴"
        text += f"{emoji} *{ag['name']}*: {ag['clicks']} clicks, CTR: {format_percent(ag['ctr'])}\n"
    await update.message.reply_text(text, parse_mode="Markdown")


@restricted
async def cmd_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Fetching...")
    terms = ads_manager.get_search_terms(min_impressions=5)
    if not terms:
        await update.message.reply_text("❌ No data")
        return
    text = "🔍 *Top Search Terms (7d)*\n\n"
    for i, t in enumerate(terms[:10], 1):
        text += f"{i}. `{t['term']}` — {t['clicks']} clicks\n"
    await update.message.reply_text(text, parse_mode="Markdown")


@restricted
async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Pausing...")
    if ads_manager.pause_campaign():
        await update.message.reply_text("⏸ Campaign paused")
    else:
        await update.message.reply_text("❌ Failed")


@restricted
async def cmd_enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Enabling...")
    if ads_manager.enable_campaign():
        await update.message.reply_text("▶️ Campaign enabled")
    else:
        await update.message.reply_text("❌ Failed")


@restricted
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""🚗 *Commands:*
/report - Report now
/status - Status
/adgroups - Ad groups
/keywords - Search terms
/pause - Pause
/enable - Enable
/start - Start monitoring
/stop - Stop monitoring""", parse_mode="Markdown")


async def post_init(application: Application):
    commands = [
        BotCommand("start", "Start monitoring"),
        BotCommand("stop", "Stop monitoring"),
        BotCommand("report", "Get report"),
        BotCommand("status", "Campaign status"),
        BotCommand("adgroups", "Ad groups"),
        BotCommand("keywords", "Search terms"),
        BotCommand("pause", "Pause campaign"),
        BotCommand("enable", "Enable campaign"),
        BotCommand("help", "Help"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("stop", cmd_stop))
    application.add_handler(CommandHandler("report", cmd_report))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("adgroups", cmd_adgroups))
    application.add_handler(CommandHandler("keywords", cmd_keywords))
    application.add_handler(CommandHandler("pause", cmd_pause))
    application.add_handler(CommandHandler("enable", cmd_enable))
    application.add_handler(CommandHandler("help", cmd_help))
    
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
