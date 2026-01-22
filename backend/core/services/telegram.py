# backend/core/services/telegram.py

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Отправка заявок в Telegram"""
    
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """Отправляет сообщение в Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured")
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                data={
                    'chat_id': self.chat_id,
                    'text': text,
                    'parse_mode': parse_mode
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    def send_booking_request(self, data: dict) -> bool:
        """Отправляет заявку на бронирование"""
        message = f"""
🚗 <b>NEW BOOKING REQUEST</b>

📍 <b>Pickup:</b> {data.get('pickup_location', 'N/A')}
📅 <b>Date:</b> {data.get('date', 'N/A')}
🕐 <b>Time:</b> {data.get('time', 'N/A')}
🚘 <b>Car Class:</b> {data.get('car_class', 'N/A')}
📍 <b>Drop-off:</b> {data.get('dropoff_location', 'N/A')}

📞 <b>Phone:</b> {data.get('phone', 'N/A')}

🌐 <b>Source:</b> {data.get('source', 'website')}
🕐 <b>Time:</b> {data.get('timestamp', 'N/A')}
"""
        return self.send_message(message)
    
    def send_contact_request(self, data: dict) -> bool:
        """Отправляет заявку с контактной формы"""
        message = f"""
📩 <b>NEW CONTACT REQUEST</b>

👤 <b>Name:</b> {data.get('first_name', '')} {data.get('last_name', '')}
📧 <b>Email:</b> {data.get('email', 'N/A')}
📞 <b>Phone:</b> {data.get('phone', 'N/A')}

💬 <b>Message:</b>
{data.get('message', 'N/A')}

🌐 <b>Source:</b> {data.get('source', 'contact_page')}
"""
        return self.send_message(message)


# Singleton instance
telegram_bot = TelegramBot()
