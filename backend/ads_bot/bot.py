"""
Prestige Cars 24 - Google Ads Telegram Bot
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional

import pytz
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
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

# Scheduler
scheduler = AsyncIOScheduler(timezone=pytz.timezone(config.TIMEZONE))
is_monitoring = False


def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"€{value:.2f}"


def format_percent(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2f}%"


def get_progress_bar(current: float, total: float, length: int = 10) -> str:
    """Generate a text progress bar"""
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
    
    # Build report
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
    
    # Alerts
    alerts = []
    
    if stats["ctr"] < config.CTR_WARNING_THRESHOLD and stats["impressions"] > 100:
        alerts.append(f"⚠️ Low CTR: {format_percent(stats['ctr'])} (< {config.CTR_WARNING_THRESHOLD}%)")
    
    if stats["avg_cpc"] > config.CPC_WARNING_THRESHOLD:
        alerts.append(f"⚠️ High CPC: {format_currency(stats['avg_cpc'])} (> €{config.CPC_WARNING_THRESHOLD})")
    
    if budget_percent > config.SPEND_WARNING_PERCENT:
        alerts.append(f"⚠️ Budget {budget_percent:.0f}% spent")
    
    # Check for underperforming ad groups
    for ag in ad_groups:
        if ag["impressions"] > 50 and ag["ctr"] < 0.5:
            alerts.append(f"⚠️ {ag['name']}: CTR only {format_percent(ag['ctr'])}")
    
    if alerts:
        report += "\n\n🚨 *Alerts:*"
        for alert in alerts[:5]:
            report += f"\n{alert}"
    else:
        report += "\n\n✅ All metrics within normal range"
    
    report += f"\n\n📍 Status: {stats['status']}"
    
    return report


async def send_scheduled_report(context: ContextTypes.DEFAULT_TYPE):
    """Send scheduled hourly report"""
    if not config.TELEGRAM_CHAT_ID:
        logger.warning("TELEGRAM_CHAT_ID not set")
        return
    
    try:
        report = await generate_report()
        await context.bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=report,
            parse_mode="Markdown"
        )
        logger.info("Scheduled report sent successfully")
    except Exception as e:
        logger.error(f"Error sending scheduled report: {e}")


# === Command Handlers ===

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - start monitoring"""
    global is_monitoring
    
    chat_id = update.effective_chat.id
    
    # Save chat_id for reports
    if not config.TELEGRAM_CHAT_ID:
        logger.info(f"Chat ID for reports: {chat_id}")
    
    welcome = f"""
🚗 *Prestige Cars 24 - Ads Monitor*

Welcome! I'll help you monitor your Google Ads campaign.

*Commands:*
/start - Start hourly monitoring
/stop - Stop monitoring
/report - Get report now
/status - Campaign status
/adgroups - Ad groups performance
/pause - Pause campaign
/enable - Enable campaign
/help - Show all commands

Your Chat ID: `{chat_id}`
_(Add this to .env.bot as TELEGRAM\\_CHAT\\_ID)_
"""
    
    await update.message.reply_text(welcome, parse_mode="Markdown")
    
    # Start scheduler if not running
    if not is_monitoring:
        scheduler.add_job(
            send_scheduled_report,
            trigger=IntervalTrigger(hours=config.REPORT_INTERVAL_HOURS),
            id="hourly_report",
            replace_existing=True,
            args=[context]
        )
        if not scheduler.running:
            scheduler.start()
        is_monitoring = True
        await update.message.reply_text(
            f"✅ Monitoring started! Reports every {config.REPORT_INTERVAL_HOURS} hour(s)."
        )
    else:
        await update.message.reply_text("ℹ️ Monitoring already active.")


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command - stop monitoring"""
    global is_monitoring
    
    if is_monitoring:
        scheduler.remove_job("hourly_report")
        is_monitoring = False
        await update.message.reply_text("⏹ Monitoring stopped.")
    else:
        await update.message.reply_text("ℹ️ Monitoring is not active.")


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command - get report now"""
    await update.message.reply_text("⏳ Generating report...")
    
    report = await generate_report()
    await update.message.reply_text(report, parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - campaign status"""
    stats = ads_manager.get_today_stats()
    
    if not stats:
        await update.message.reply_text("❌ Failed to fetch status")
        return
    
    status_text = f"""
📍 *Campaign Status*

Campaign: {stats["campaign_name"]}
Status: {stats["status"]}

Today:
• Spend: {format_currency(stats["cost"])} / {format_currency(config.DAILY_BUDGET)}
• Clicks: {stats["clicks"]}
• Conversions: {stats["conversions"]}
"""
    
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def cmd_adgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /adgroups command - show ad groups stats"""
    ad_groups = ads_manager.get_ad_group_stats()
    
    if not ad_groups:
        await update.message.reply_text("❌ No ad group data available")
        return
    
    text = "📊 *Ad Groups Performance (Today)*\n\n"
    
    for ag in ad_groups:
        emoji = "🟢" if ag["ctr"] >= 1.0 else "🟡" if ag["ctr"] >= 0.5 else "🔴"
        text += f"{emoji} *{ag['name']}*\n"
        text += f"   {ag['clicks']} clicks | {format_currency(ag['cost'])} | CTR: {format_percent(ag['ctr'])}\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pause command - pause campaign"""
    await update.message.reply_text("⏳ Pausing campaign...")
    
    success = ads_manager.pause_campaign()
    
    if success:
        await update.message.reply_text("⏸ Campaign paused successfully")
    else:
        await update.message.reply_text("❌ Failed to pause campaign (check API credentials)")


async def cmd_enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /enable command - enable campaign"""
    await update.message.reply_text("⏳ Enabling campaign...")
    
    success = ads_manager.enable_campaign()
    
    if success:
        await update.message.reply_text("▶️ Campaign enabled successfully")
    else:
        await update.message.reply_text("❌ Failed to enable campaign (check API credentials)")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🚗 *Prestige Cars 24 - Ads Bot*

*Monitoring:*
/start - Start hourly reports
/stop - Stop reports

*Reports:*
/report - Get report now
/status - Campaign status
/adgroups - Ad groups performance

*Control:*
/pause - Pause campaign
/enable - Enable campaign

*Settings:*
Report interval: {interval}h
Campaign: {campaign}
Budget: {budget}/day
""".format(
        interval=config.REPORT_INTERVAL_HOURS,
        campaign=config.CAMPAIGN_NAME,
        budget=format_currency(config.DAILY_BUDGET)
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def post_init(application: Application):
    """Set bot commands in Telegram menu"""
    commands = [
        BotCommand("start", "Start monitoring"),
        BotCommand("stop", "Stop monitoring"),
        BotCommand("report", "Get report now"),
        BotCommand("status", "Campaign status"),
        BotCommand("adgroups", "Ad groups stats"),
        BotCommand("pause", "Pause campaign"),
        BotCommand("enable", "Enable campaign"),
        BotCommand("help", "Show help"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    """Main function to run the bot"""
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    # Build application
    application = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("stop", cmd_stop))
    application.add_handler(CommandHandler("report", cmd_report))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("adgroups", cmd_adgroups))
    application.add_handler(CommandHandler("pause", cmd_pause))
    application.add_handler(CommandHandler("enable", cmd_enable))
    application.add_handler(CommandHandler("help", cmd_help))
    
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
