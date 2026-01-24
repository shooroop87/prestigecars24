import os
import requests


def send_telegram(message):
    """Отправка в Telegram только разрешённым пользователям"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    allowed_ids = os.getenv('TELEGRAM_CHAT_ID', '')
    
    if not token or not allowed_ids:
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    allowed_list = [cid.strip() for cid in allowed_ids.split(',') if cid.strip()]
    
    if not allowed_list:
        return False
    
    success = True
    for chat_id in allowed_list:
        try:
            requests.post(url, data={
                'chat_id': chat_id, 
                'text': message, 
                'parse_mode': 'HTML'
            })
        except:
            success = False
    
    return success