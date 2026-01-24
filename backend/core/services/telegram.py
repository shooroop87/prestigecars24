import os
import requests


def send_telegram(message):
    """Отправка в Telegram нескольким получателям"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_ids = os.getenv('TELEGRAM_CHAT_ID', '')
    
    if not token or not chat_ids:
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    success = True
    
    for chat_id in chat_ids.split(','):
        chat_id = chat_id.strip()
        if not chat_id:
            continue
        try:
            requests.post(url, data={
                'chat_id': chat_id, 
                'text': message, 
                'parse_mode': 'HTML'
            })
        except:
            success = False
    
    return success